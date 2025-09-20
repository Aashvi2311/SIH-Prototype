from app.models import Certificate, Institution, VerificationLog, SuspiciousActivity
from app.ocr_utils import DocumentProcessor
from app import db
from fuzzywuzzy import fuzz, process
import re
from datetime import datetime
import os

class CertificateVerifier:
    """Main verification engine for certificate authenticity"""
    
    def __init__(self):
        self.processor = DocumentProcessor()
        
        # Thresholds for matching
        self.name_threshold = 80  # Fuzzy matching threshold for names
        self.course_threshold = 75  # Fuzzy matching threshold for courses
        self.minimum_confidence = 60  # Minimum confidence for valid certificate
    
    def normalize_text(self, text):
        """Normalize text for better matching"""
        if not text:
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Remove common prefixes and suffixes
        normalized = re.sub(r'^(mr\.?|ms\.?|dr\.?)\s+', '', normalized)
        normalized = re.sub(r'\s+(jr\.?|sr\.?|ii|iii)$', '', normalized)
        
        return normalized
    
    def fuzzy_match_name(self, extracted_name, db_name):
        """Perform fuzzy matching on names"""
        if not extracted_name or not db_name:
            return 0
        
        # Normalize both names
        norm_extracted = self.normalize_text(extracted_name)
        norm_db = self.normalize_text(db_name)
        
        # Calculate similarity score
        ratio = fuzz.ratio(norm_extracted, norm_db)
        token_ratio = fuzz.token_sort_ratio(norm_extracted, norm_db)
        partial_ratio = fuzz.partial_ratio(norm_extracted, norm_db)
        
        # Use the highest score
        return max(ratio, token_ratio, partial_ratio)
    
    def fuzzy_match_course(self, extracted_course, db_course):
        """Perform fuzzy matching on course names"""
        if not extracted_course or not db_course:
            return 0
        
        # Normalize course names
        norm_extracted = self.normalize_text(extracted_course)
        norm_db = self.normalize_text(db_course)
        
        # Calculate similarity score
        return fuzz.token_sort_ratio(norm_extracted, norm_db)
    
    def find_matching_certificates(self, extracted_data):
        """Find potential matching certificates in the database"""
        potential_matches = []
        
        # Get all certificates from database
        all_certificates = Certificate.query.all()
        
        for cert in all_certificates:
            match_score = 0
            match_details = {}
            
            # Check certificate number (exact match preferred)
            if 'certificate_number' in extracted_data:
                if extracted_data['certificate_number'].upper() == cert.certificate_number.upper():
                    match_score += 40  # High weight for exact cert number match
                    match_details['certificate_number_match'] = 'EXACT'
                else:
                    # Partial match for certificate number
                    partial_score = fuzz.ratio(extracted_data['certificate_number'].upper(), 
                                             cert.certificate_number.upper())
                    if partial_score > 80:
                        match_score += 20
                        match_details['certificate_number_match'] = 'PARTIAL'
            
            # Check student name
            if 'student_name' in extracted_data:
                name_score = self.fuzzy_match_name(extracted_data['student_name'], cert.student_name)
                if name_score > self.name_threshold:
                    match_score += 25
                    match_details['name_match_score'] = name_score
            
            # Check roll number
            if 'roll_number' in extracted_data and cert.student_roll_number:
                if extracted_data['roll_number'].upper() == cert.student_roll_number.upper():
                    match_score += 20
                    match_details['roll_number_match'] = 'EXACT'
            
            # Check course name
            if 'course' in extracted_data:
                course_score = self.fuzzy_match_course(extracted_data['course'], cert.course_name)
                if course_score > self.course_threshold:
                    match_score += 15
                    match_details['course_match_score'] = course_score
            
            # Check passing year
            if 'year' in extracted_data:
                try:
                    extracted_year = int(extracted_data['year'])
                    if extracted_year == cert.passing_year:
                        match_score += 10
                        match_details['year_match'] = 'EXACT'
                    elif abs(extracted_year - cert.passing_year) <= 1:
                        match_score += 5  # Allow 1 year difference
                        match_details['year_match'] = 'CLOSE'
                except ValueError:
                    pass
            
            # If there's a reasonable match, add to potential matches
            if match_score >= 30:  # Minimum threshold for consideration
                potential_matches.append({
                    'certificate': cert,
                    'match_score': match_score,
                    'match_details': match_details
                })
        
        # Sort by match score (highest first)
        potential_matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        return potential_matches
    
    def detect_anomalies(self, extracted_data, matched_certificate=None):
        """Detect various types of anomalies in the certificate"""
        flags = []
        
        # Check for impossible dates
        if 'year' in extracted_data:
            try:
                year = int(extracted_data['year'])
                current_year = datetime.now().year
                
                if year > current_year:
                    flags.append('FUTURE_DATE')
                elif year < 1950:  # Unreasonably old
                    flags.append('INVALID_DATE')
            except ValueError:
                flags.append('INVALID_YEAR_FORMAT')
        
        # Check for suspicious grade/percentage combinations
        if 'grade' in extracted_data and 'percentage' in extracted_data:
            try:
                percentage = float(extracted_data['percentage'])
                grade = extracted_data['grade'].upper()
                
                # Basic grade-percentage consistency check
                if grade == 'A' and percentage < 80:
                    flags.append('GRADE_PERCENTAGE_MISMATCH')
                elif grade == 'B' and (percentage < 60 or percentage >= 80):
                    flags.append('GRADE_PERCENTAGE_MISMATCH')
                elif grade == 'C' and (percentage < 40 or percentage >= 60):
                    flags.append('GRADE_PERCENTAGE_MISMATCH')
            except ValueError:
                flags.append('INVALID_PERCENTAGE_FORMAT')
        
        # Check against matched certificate if available
        if matched_certificate:
            cert = matched_certificate['certificate']
            
            # Check if institution is active
            if not cert.institution.is_active:
                flags.append('INACTIVE_INSTITUTION')
            
            # Check for exact matches that should be identical
            if ('certificate_number' in extracted_data and 
                extracted_data['certificate_number'].upper() == cert.certificate_number.upper()):
                
                # If cert number matches exactly, other details should too
                if ('student_name' in extracted_data and 
                    self.fuzzy_match_name(extracted_data['student_name'], cert.student_name) < 95):
                    flags.append('CERT_NUMBER_NAME_MISMATCH')
                
                if ('year' in extracted_data and 
                    int(extracted_data['year']) != cert.passing_year):
                    flags.append('CERT_NUMBER_YEAR_MISMATCH')
        
        return flags
    
    def calculate_verification_status(self, potential_matches, anomaly_flags, forgery_flags):
        """Determine the final verification status"""
        
        # Check for critical issues first
        critical_flags = ['FUTURE_DATE', 'INACTIVE_INSTITUTION', 'CERT_NUMBER_NAME_MISMATCH']
        if any(flag in anomaly_flags + forgery_flags for flag in critical_flags):
            return 'INVALID', 10
        
        # If no matches found
        if not potential_matches:
            if len(anomaly_flags + forgery_flags) > 2:
                return 'INVALID', 20
            else:
                return 'SUSPICIOUS', 30
        
        # Get best match
        best_match = potential_matches[0]
        match_score = best_match['match_score']
        
        # Determine status based on match score and flags
        if match_score >= 80 and len(anomaly_flags + forgery_flags) == 0:
            return 'VALID', 95
        elif match_score >= 70 and len(anomaly_flags + forgery_flags) <= 1:
            return 'VALID', 85
        elif match_score >= 60 and len(anomaly_flags + forgery_flags) <= 2:
            return 'SUSPICIOUS', 70
        else:
            return 'INVALID', 40
    
    def verify_certificate(self, file_path, filename, ip_address=None, user_agent=None):
        """Main verification method"""
        
        try:
            # Process the document
            processing_result = self.processor.process_document(file_path, filename)
            
            if 'error' in processing_result:
                # Log error
                log = VerificationLog(
                    uploaded_filename=filename,
                    verification_status='ERROR',
                    extracted_data={'error': processing_result['error']},
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                db.session.add(log)
                db.session.commit()
                
                return {
                    'status': 'ERROR',
                    'message': 'Failed to process document',
                    'error': processing_result['error']
                }
            
            extracted_data = processing_result['extracted_data']
            forgery_flags = processing_result['forgery_flags']
            
            # Find matching certificates
            potential_matches = self.find_matching_certificates(extracted_data)
            
            # Detect anomalies
            best_match = potential_matches[0] if potential_matches else None
            anomaly_flags = self.detect_anomalies(extracted_data, best_match)
            
            # Calculate final verification status
            verification_status, confidence_score = self.calculate_verification_status(
                potential_matches, anomaly_flags, forgery_flags
            )
            
            # Create verification log
            log = VerificationLog(
                uploaded_filename=filename,
                file_hash=processing_result['file_hash'],
                extracted_data=extracted_data,
                verification_status=verification_status,
                confidence_score=confidence_score,
                matched_certificate_id=best_match['certificate'].id if best_match else None,
                flags=anomaly_flags + forgery_flags,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            db.session.add(log)
            db.session.flush()  # To get the log ID
            
            # Create suspicious activity records if needed
            if verification_status in ['INVALID', 'SUSPICIOUS']:
                for flag in anomaly_flags + forgery_flags:
                    suspicious_activity = SuspiciousActivity(
                        verification_log_id=log.id,
                        activity_type=flag,
                        description=f"Detected {flag} in certificate verification",
                        severity='HIGH' if verification_status == 'INVALID' else 'MEDIUM'
                    )
                    db.session.add(suspicious_activity)
            
            db.session.commit()
            
            # Prepare response
            result = {
                'status': verification_status,
                'confidence_score': confidence_score,
                'extracted_data': extracted_data,
                'flags': anomaly_flags + forgery_flags,
                'log_id': log.id
            }
            
            if best_match:
                cert = best_match['certificate']
                result['matched_certificate'] = {
                    'id': cert.id,
                    'certificate_number': cert.certificate_number,
                    'student_name': cert.student_name,
                    'course_name': cert.course_name,
                    'institution_name': cert.institution.name,
                    'passing_year': cert.passing_year,
                    'match_score': best_match['match_score'],
                    'match_details': best_match['match_details']
                }
            
            return result
            
        except Exception as e:
            # Log unexpected errors
            log = VerificationLog(
                uploaded_filename=filename,
                verification_status='ERROR',
                extracted_data={'error': str(e)},
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(log)
            db.session.commit()
            
            return {
                'status': 'ERROR',
                'message': 'Unexpected error during verification',
                'error': str(e)
            }
