import pytesseract
import cv2
import numpy as np
from PIL import Image
import PyPDF2
import io
import re
import hashlib
from datetime import datetime
import os

class DocumentProcessor:
    """Class to handle OCR and document processing for certificate verification"""
    
    def __init__(self):
        # Configure tesseract for better OCR results
        self.tesseract_config = r'--oem 3 --psm 6'
        
        # Common patterns for certificate data extraction
        self.patterns = {
            'certificate_number': [
                r'certificate\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'cert\.?\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'registration\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'reg\.?\s+no\.?\s*:?\s*([A-Z0-9/\-]+)'
            ],
            'student_name': [
                r'name\s*:?\s*([A-Za-z\s]+)',
                r'student\s+name\s*:?\s*([A-Za-z\s]+)',
                r'this\s+is\s+to\s+certify\s+that\s+([A-Za-z\s]+)',
                r'mr\.?\s*\/?\s*ms\.?\s*([A-Za-z\s]+)'
            ],
            'roll_number': [
                r'roll\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'enrollment\s+no\.?\s*:?\s*([A-Z0-9/\-]+)',
                r'student\s+id\s*:?\s*([A-Z0-9/\-]+)'
            ],
            'course': [
                r'course\s*:?\s*([A-Za-z\s]+)',
                r'degree\s*:?\s*([A-Za-z\s]+)',
                r'bachelor\s+of\s+([A-Za-z\s]+)',
                r'master\s+of\s+([A-Za-z\s]+)',
                r'diploma\s+in\s+([A-Za-z\s]+)'
            ],
            'year': [
                r'year\s*:?\s*(\d{4})',
                r'passing\s+year\s*:?\s*(\d{4})',
                r'session\s*:?\s*(\d{4})',
                r'(\d{4})\s*session'
            ],
            'grade': [
                r'grade\s*:?\s*([A-Z]+)',
                r'class\s*:?\s*([A-Z\s]+)',
                r'division\s*:?\s*([A-Z\s]+)'
            ],
            'percentage': [
                r'(\d+\.?\d*)\s*%',
                r'marks?\s*:?\s*(\d+\.?\d*)',
                r'percentage\s*:?\s*(\d+\.?\d*)'
            ]
        }
    
    def calculate_file_hash(self, file_content):
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    def preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        try:
            # Convert PIL image to OpenCV format
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply image enhancements
            # 1. Noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # 2. Contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 3. Threshold to binary image
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
        except Exception as e:
            print(f"Error in image preprocessing: {str(e)}")
            return np.array(image)
    
    def extract_text_from_image(self, image_path):
        """Extract text from image using OCR"""
        try:
            # Load and preprocess image
            image = Image.open(image_path)
            processed_image = self.preprocess_image(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return text.strip()
        except Exception as e:
            print(f"Error in image OCR: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF file"""
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            print(f"Error in PDF text extraction: {str(e)}")
            return ""
    
    def extract_data_patterns(self, text):
        """Extract structured data from text using regex patterns"""
        extracted_data = {}
        
        # Clean the text
        text_clean = re.sub(r'\s+', ' ', text.lower().strip())
        
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_clean, re.IGNORECASE)
                if match:
                    extracted_data[field] = match.group(1).strip()
                    break  # Use first matching pattern
        
        return extracted_data
    
    def detect_common_forgery_patterns(self, text):
        """Detect common patterns that might indicate forgery"""
        flags = []
        
        # Check for suspicious formatting
        if len(re.findall(r'[A-Z]{10,}', text)) > 3:  # Too many all-caps words
            flags.append("SUSPICIOUS_FORMATTING")
        
        # Check for common typos in institution names
        suspicious_words = ['universtiy', 'colege', 'instutute', 'certficate']
        for word in suspicious_words:
            if word in text.lower():
                flags.append("SPELLING_ERRORS")
                break
        
        # Check for missing common fields
        required_fields = ['certificate', 'name', 'year']
        missing_count = sum(1 for field in required_fields if field not in text.lower())
        if missing_count > 1:
            flags.append("MISSING_REQUIRED_FIELDS")
        
        return flags
    
    def process_document(self, file_path, filename):
        """Main method to process uploaded document"""
        try:
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_content = f.read()
                file_hash = self.calculate_file_hash(file_content)
            
            # Determine file type and extract text
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                extracted_text = self.extract_text_from_pdf(file_path)
            elif file_extension in ['png', 'jpg', 'jpeg']:
                extracted_text = self.extract_text_from_image(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Extract structured data
            structured_data = self.extract_data_patterns(extracted_text)
            
            # Detect potential forgery indicators
            forgery_flags = self.detect_common_forgery_patterns(extracted_text)
            
            return {
                'file_hash': file_hash,
                'raw_text': extracted_text,
                'extracted_data': structured_data,
                'forgery_flags': forgery_flags,
                'processed_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'processed_at': datetime.now().isoformat()
            }
