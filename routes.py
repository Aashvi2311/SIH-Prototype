from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from app.models import Institution, Certificate, VerificationLog, SuspiciousActivity
from app.verification_engine import CertificateVerifier
from app import db
import os
from datetime import datetime, date

main = Blueprint('main', __name__)

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', 'pdf,png,jpg,jpeg').split(',')
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@main.route('/')
def index():
    """Home page with upload interface"""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_certificate():
    """Handle certificate upload and verification"""
    try:
        if 'certificate' not in request.files:
            return jsonify({'status': 'error', 'message': 'No file uploaded'}), 400
        
        file = request.files['certificate']
        if file.filename == '':
            return jsonify({'status': 'error', 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'status': 'error', 'message': 'Invalid file type. Only PDF, PNG, JPG, JPEG allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Get client info
        ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        user_agent = request.headers.get('User-Agent', '')
        
        # Verify certificate
        verifier = CertificateVerifier()
        result = verifier.verify_certificate(file_path, filename, ip_address, user_agent)
        
        # Clean up uploaded file
        try:
            os.remove(file_path)
        except:
            pass
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@main.route('/dashboard')
def dashboard():
    """Admin dashboard showing verification statistics"""
    # Get recent verification logs
    recent_logs = VerificationLog.query.order_by(VerificationLog.created_at.desc()).limit(20).all()
    
    # Get verification statistics
    total_verifications = VerificationLog.query.count()
    valid_count = VerificationLog.query.filter_by(verification_status='VALID').count()
    invalid_count = VerificationLog.query.filter_by(verification_status='INVALID').count()
    suspicious_count = VerificationLog.query.filter_by(verification_status='SUSPICIOUS').count()
    
    # Get suspicious activities
    suspicious_activities = SuspiciousActivity.query.filter_by(status='PENDING').order_by(SuspiciousActivity.created_at.desc()).limit(10).all()
    
    # Get institution stats
    total_institutions = Institution.query.count()
    active_institutions = Institution.query.filter_by(is_active=True).count()
    
    stats = {
        'total_verifications': total_verifications,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'suspicious_count': suspicious_count,
        'total_institutions': total_institutions,
        'active_institutions': active_institutions
    }
    
    return render_template('dashboard.html', 
                         recent_logs=recent_logs, 
                         stats=stats, 
                         suspicious_activities=suspicious_activities)

@main.route('/institutions')
def institutions():
    """List all institutions"""
    institutions = Institution.query.order_by(Institution.name).all()
    return render_template('institutions.html', institutions=institutions)

@main.route('/add_institution', methods=['GET', 'POST'])
def add_institution():
    """Add new institution"""
    if request.method == 'POST':
        try:
            institution = Institution(
                name=request.form['name'],
                code=request.form['code'],
                type=request.form['type'],
                address=request.form.get('address', ''),
                contact_email=request.form.get('contact_email', ''),
                phone=request.form.get('phone', ''),
                established_year=int(request.form['established_year']) if request.form.get('established_year') else None
            )
            
            db.session.add(institution)
            db.session.commit()
            
            flash('Institution added successfully!', 'success')
            return redirect(url_for('main.institutions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding institution: {str(e)}', 'danger')
    
    return render_template('add_institution.html')

@main.route('/add_certificate', methods=['GET', 'POST'])
def add_certificate():
    """Add new certificate to database"""
    institutions = Institution.query.filter_by(is_active=True).order_by(Institution.name).all()
    
    if request.method == 'POST':
        try:
            # Parse issue date
            issue_date_str = request.form['issue_date']
            issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            
            certificate = Certificate(
                certificate_number=request.form['certificate_number'],
                student_name=request.form['student_name'],
                student_roll_number=request.form.get('student_roll_number', ''),
                course_name=request.form['course_name'],
                degree_type=request.form['degree_type'],
                passing_year=int(request.form['passing_year']),
                grade=request.form.get('grade', ''),
                percentage=float(request.form['percentage']) if request.form.get('percentage') else None,
                issue_date=issue_date,
                institution_id=int(request.form['institution_id'])
            )
            
            db.session.add(certificate)
            db.session.commit()
            
            flash('Certificate added successfully!', 'success')
            return redirect(url_for('main.certificates'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding certificate: {str(e)}', 'danger')
    
    return render_template('add_certificate.html', institutions=institutions)

@main.route('/certificates')
def certificates():
    """List all certificates"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    certificates = Certificate.query.join(Institution).order_by(Certificate.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('certificates.html', certificates=certificates)

@main.route('/verification_logs')
def verification_logs():
    """List verification logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    logs = VerificationLog.query.order_by(VerificationLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('verification_logs.html', logs=logs)

@main.route('/log/<int:log_id>')
def view_log(log_id):
    """View detailed verification log"""
    log = VerificationLog.query.get_or_404(log_id)
    return render_template('log_detail.html', log=log)

@main.route('/suspicious_activities')
def suspicious_activities():
    """List suspicious activities"""
    activities = SuspiciousActivity.query.order_by(SuspiciousActivity.created_at.desc()).all()
    return render_template('suspicious_activities.html', activities=activities)

@main.route('/api/stats')
def api_stats():
    """API endpoint for verification statistics"""
    total_verifications = VerificationLog.query.count()
    valid_count = VerificationLog.query.filter_by(verification_status='VALID').count()
    invalid_count = VerificationLog.query.filter_by(verification_status='INVALID').count()
    suspicious_count = VerificationLog.query.filter_by(verification_status='SUSPICIOUS').count()
    
    return jsonify({
        'total_verifications': total_verifications,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'suspicious_count': suspicious_count
    })

@main.route('/help')
def help_page():
    """Help page with usage instructions"""
    return render_template('help.html')
