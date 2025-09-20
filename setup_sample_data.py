#!/usr/bin/env python3
"""
Script to populate the database with sample institutions and certificates
for testing the Certificate Verification System MVP
"""

from app import create_app, db
from app.models import Institution, Certificate
from datetime import date
import sys

def create_sample_data():
    """Create sample institutions and certificates"""
    
    print("Creating sample institutions...")
    
    # Sample institutions in Jharkhand
    institutions_data = [
        {
            'name': 'Ranchi University',
            'code': 'RU001',
            'type': 'University',
            'address': 'Ranchi, Jharkhand',
            'contact_email': 'info@ranchiuniversity.ac.in',
            'phone': '+91-651-2234567',
            'established_year': 1960
        },
        {
            'name': 'Birla Institute of Technology',
            'code': 'BIT001',
            'type': 'Institute',
            'address': 'Mesra, Ranchi, Jharkhand',
            'contact_email': 'admissions@bitmesra.ac.in',
            'phone': '+91-651-2275444',
            'established_year': 1955
        },
        {
            'name': 'Central University of Jharkhand',
            'code': 'CUJ001',
            'type': 'University',
            'address': 'Brambe, Ranchi, Jharkhand',
            'contact_email': 'info@cuj.ac.in',
            'phone': '+91-651-2835577',
            'established_year': 2009
        },
        {
            'name': 'St. Xaviers College',
            'code': 'SXC001',
            'type': 'College',
            'address': 'Doranda, Ranchi, Jharkhand',
            'contact_email': 'info@stxaviersranchi.ac.in',
            'phone': '+91-651-2460987',
            'established_year': 1944
        },
        {
            'name': 'Government Polytechnic Ranchi',
            'code': 'GPR001',
            'type': 'Polytechnic',
            'address': 'Ranchi, Jharkhand',
            'contact_email': 'gpr@gov.jh.in',
            'phone': '+91-651-2567890',
            'established_year': 1960
        }
    ]
    
    institutions = []
    for inst_data in institutions_data:
        institution = Institution(**inst_data)
        db.session.add(institution)
        institutions.append(institution)
    
    db.session.commit()
    print(f"Created {len(institutions)} sample institutions")
    
    print("Creating sample certificates...")
    
    # Sample certificates
    certificates_data = [
        # Ranchi University certificates
        {
            'certificate_number': 'RU/2023/BSC/001234',
            'student_name': 'Rahul Kumar Singh',
            'student_roll_number': 'RU23BSC001234',
            'course_name': 'Bachelor of Science in Computer Science',
            'degree_type': 'Bachelor',
            'passing_year': 2023,
            'grade': 'A',
            'percentage': 85.5,
            'issue_date': date(2023, 6, 15),
            'institution_id': institutions[0].id
        },
        {
            'certificate_number': 'RU/2022/BA/005678',
            'student_name': 'Priya Kumari',
            'student_roll_number': 'RU22BA005678',
            'course_name': 'Bachelor of Arts in English',
            'degree_type': 'Bachelor',
            'passing_year': 2022,
            'grade': 'B',
            'percentage': 75.2,
            'issue_date': date(2022, 7, 20),
            'institution_id': institutions[0].id
        },
        
        # BIT Mesra certificates
        {
            'certificate_number': 'BIT/2023/BTECH/098765',
            'student_name': 'Ankit Sharma',
            'student_roll_number': 'BIT23BTECH098765',
            'course_name': 'Bachelor of Technology in Computer Science and Engineering',
            'degree_type': 'Bachelor',
            'passing_year': 2023,
            'grade': 'A+',
            'percentage': 92.3,
            'issue_date': date(2023, 5, 30),
            'institution_id': institutions[1].id
        },
        {
            'certificate_number': 'BIT/2023/MTECH/012345',
            'student_name': 'Deepika Verma',
            'student_roll_number': 'BIT23MTECH012345',
            'course_name': 'Master of Technology in Information Technology',
            'degree_type': 'Master',
            'passing_year': 2023,
            'grade': 'A',
            'percentage': 88.7,
            'issue_date': date(2023, 6, 10),
            'institution_id': institutions[1].id
        },
        
        # Central University of Jharkhand certificates
        {
            'certificate_number': 'CUJ/2023/MA/567890',
            'student_name': 'Ravi Kumar',
            'student_roll_number': 'CUJ23MA567890',
            'course_name': 'Master of Arts in Economics',
            'degree_type': 'Master',
            'passing_year': 2023,
            'grade': 'B+',
            'percentage': 78.9,
            'issue_date': date(2023, 7, 5),
            'institution_id': institutions[2].id
        },
        
        # St. Xaviers College certificates
        {
            'certificate_number': 'SXC/2023/BCOM/111222',
            'student_name': 'Sunita Devi',
            'student_roll_number': 'SXC23BCOM111222',
            'course_name': 'Bachelor of Commerce',
            'degree_type': 'Bachelor',
            'passing_year': 2023,
            'grade': 'A',
            'percentage': 82.1,
            'issue_date': date(2023, 6, 25),
            'institution_id': institutions[3].id
        },
        
        # Government Polytechnic certificates
        {
            'certificate_number': 'GPR/2023/DIP/333444',
            'student_name': 'Amit Kumar',
            'student_roll_number': 'GPR23DIP333444',
            'course_name': 'Diploma in Mechanical Engineering',
            'degree_type': 'Diploma',
            'passing_year': 2023,
            'grade': 'B',
            'percentage': 72.5,
            'issue_date': date(2023, 8, 1),
            'institution_id': institutions[4].id
        }
    ]
    
    for cert_data in certificates_data:
        certificate = Certificate(**cert_data)
        db.session.add(certificate)
    
    db.session.commit()
    print(f"Created {len(certificates_data)} sample certificates")
    
    print("\nSample data created successfully!")
    print("\nSample certificates for testing:")
    print("=" * 50)
    
    for i, cert in enumerate(certificates_data, 1):
        print(f"{i}. {cert['student_name']}")
        print(f"   Certificate: {cert['certificate_number']}")
        print(f"   Course: {cert['course_name']}")
        print(f"   Institution: {institutions_data[cert['institution_id']-1]['name']}")
        print(f"   Year: {cert['passing_year']}")
        print()

def main():
    """Main function"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if data already exists
            if Institution.query.count() > 0 or Certificate.query.count() > 0:
                response = input("Sample data already exists. Do you want to recreate it? (y/N): ")
                if response.lower() != 'y':
                    print("Cancelled.")
                    return
                
                # Clear existing data
                Certificate.query.delete()
                Institution.query.delete()
                db.session.commit()
                print("Cleared existing sample data.")
            
            create_sample_data()
            
        except Exception as e:
            print(f"Error creating sample data: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    main()
