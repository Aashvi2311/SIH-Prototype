from app import db
from datetime import datetime
from sqlalchemy import Text, JSON

class Institution(db.Model):
    """Model for educational institutions in Jharkhand"""
    __tablename__ = 'institutions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    type = db.Column(db.String(50), nullable=False)  # University, College, Institute
    address = db.Column(Text)
    contact_email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    established_year = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with certificates
    certificates = db.relationship('Certificate', backref='institution', lazy=True)
    
    def __repr__(self):
        return f'<Institution {self.name}>'

class Certificate(db.Model):
    """Model for valid certificates issued by institutions"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_number = db.Column(db.String(50), nullable=False)
    student_name = db.Column(db.String(100), nullable=False)
    student_roll_number = db.Column(db.String(50))
    course_name = db.Column(db.String(200), nullable=False)
    degree_type = db.Column(db.String(50), nullable=False)  # Bachelor, Master, Diploma, etc.
    passing_year = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(20))
    percentage = db.Column(db.Float)
    issue_date = db.Column(db.Date, nullable=False)
    
    # Foreign key to institution
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    
    # Additional metadata
    cert_metadata = db.Column(JSON)  # Store additional certificate details as JSON
    
    # Security features
    certificate_hash = db.Column(db.String(64))  # SHA-256 hash for verification
    digital_signature = db.Column(Text)  # Digital signature if available
    qr_code_data = db.Column(Text)  # QR code content if present
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (db.UniqueConstraint('certificate_number', 'institution_id'),)
    
    def __repr__(self):
        return f'<Certificate {self.certificate_number} - {self.student_name}>'

class VerificationLog(db.Model):
    """Model to log all verification attempts"""
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    uploaded_filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64))
    
    # Extracted data from OCR
    extracted_data = db.Column(JSON)
    
    # Verification results
    verification_status = db.Column(db.String(20), nullable=False)  # VALID, INVALID, SUSPICIOUS, ERROR
    confidence_score = db.Column(db.Float, default=0.0)
    matched_certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'))
    
    # Flags for different types of issues
    flags = db.Column(JSON)  # Store detected issues as JSON array
    
    # Request metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with matched certificate
    matched_certificate = db.relationship('Certificate', backref='verification_logs')
    
    def __repr__(self):
        return f'<VerificationLog {self.uploaded_filename} - {self.verification_status}>'

class SuspiciousActivity(db.Model):
    """Model to track suspicious verification attempts"""
    __tablename__ = 'suspicious_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    verification_log_id = db.Column(db.Integer, db.ForeignKey('verification_logs.id'), nullable=False)
    
    # Types of suspicious activity
    activity_type = db.Column(db.String(50), nullable=False)  # FORGED_SIGNATURE, INVALID_SEAL, etc.
    description = db.Column(Text)
    severity = db.Column(db.String(10), default='MEDIUM')  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Investigation status
    status = db.Column(db.String(20), default='PENDING')  # PENDING, INVESTIGATING, RESOLVED, FALSE_POSITIVE
    investigated_by = db.Column(db.String(100))
    investigation_notes = db.Column(Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with verification log
    verification_log = db.relationship('VerificationLog', backref='suspicious_activities')
    
    def __repr__(self):
        return f'<SuspiciousActivity {self.activity_type} - {self.severity}>'
