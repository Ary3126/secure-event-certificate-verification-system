from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
import os
import json
from datetime import datetime
import csv
import pandas as pd
from werkzeug.utils import secure_filename
from .models import Admin, Student, Template, Certificate, db
from .certificate_generator import CertificateGenerator
from .auth import login_required, admin_required, student_required

main_bp = Blueprint('main', __name__)

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard"""
    user_id = session.get('user_id')
    user = Admin.query.get(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    templates_count = Template.query.filter_by(admin_id=user_id, is_active=True).count()
    certificates_count = Certificate.query.filter_by(admin_id=user_id).count()
    total_verifications = sum([cert.verification_count for cert in Certificate.query.filter_by(admin_id=user_id).all()])
    
    return render_template('dashboard.html',
                         user=user,
                         templates_count=templates_count,
                         certificates_count=certificates_count,
                         total_verifications=total_verifications)


@main_bp.route('/student/dashboard')
@student_required
def student_dashboard():
    """Student dashboard - show student's certificates"""
    user_id = session.get('user_id')
    user = Student.query.get(user_id)
    
    if not user:
        return redirect(url_for('auth.login'))
    
    page = request.args.get('page', 1, type=int)
    certificates = Certificate.query.filter_by(student_id=user_id).paginate(page=page, per_page=20)
    return render_template('certificates_list.html', certificates=certificates)

@main_bp.route('/template/manage')
@admin_required
def manage_templates():
    """Manage certificate templates"""
    user_id = session.get('user_id')
    templates = Template.query.filter_by(admin_id=user_id, is_active=True).all()
    
    return render_template('template_manager.html', templates=templates)

@main_bp.route('/template/upload', methods=['POST'])
@admin_required
def upload_template():
    """Upload new certificate template"""
    user_id = session.get('user_id')
    
    if 'template_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('main.manage_templates'))
    
    file = request.files['template_file']
    template_name = request.form.get('template_name', '').strip()
    field_config = request.form.get('field_config', '{}')
    
    if not template_name:
        flash('Template name is required', 'danger')
        return redirect(url_for('main.manage_templates'))
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('main.manage_templates'))
    
    if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg'}):
        filename = secure_filename(f"{user_id}_{datetime.now().timestamp()}_{file.filename}")
        upload_folder = os.path.join(os.path.dirname(__file__), '..', 'templates_upload')
        
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            template = Template(
                admin_id=user_id,
                template_name=template_name,
                background_path=filepath,
                field_configuration=json.loads(field_config)
            )
            db.session.add(template)
            db.session.commit()
            flash(f'Template "{template_name}" uploaded successfully', 'success')
        except Exception as e:
            db.session.rollback()
            if os.path.exists(filepath):
                os.remove(filepath)
            flash('Error uploading template', 'danger')
    else:
        flash('Only PNG and JPG files are allowed', 'danger')
    
    return redirect(url_for('main.manage_templates'))

@main_bp.route('/template/delete/<int:template_id>', methods=['POST'])
@admin_required
def delete_template(template_id):
    """Delete template"""
    user_id = session.get('user_id')
    template = Template.query.filter_by(id=template_id, admin_id=user_id).first()
    
    if not template:
        flash('Template not found', 'danger')
        return redirect(url_for('main.manage_templates'))
    
    try:
        # Remove background file
        if template.background_path and os.path.exists(template.background_path):
            os.remove(template.background_path)
        
        template.is_active = False
        db.session.commit()
        flash('Template deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting template', 'danger')
    
    return redirect(url_for('main.manage_templates'))

@main_bp.route('/certificates/generate', methods=['GET', 'POST'])
@admin_required
def generate_certificates():
    """Generate certificates from CSV"""
    user_id = session.get('user_id')
    templates = Template.query.filter_by(admin_id=user_id, is_active=True).all()
    
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No CSV file selected', 'danger')
            return redirect(url_for('main.generate_certificates'))
        
        file = request.files['csv_file']
        template_id = request.form.get('template_id', '')
        
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('main.generate_certificates'))
        
        if file and allowed_file(file.filename, {'csv'}):
            try:
                # Read CSV
                df = pd.read_csv(file)
                
                # Validate CSV
                required_columns = ['name', 'course', 'email']
                if not all(col in df.columns for col in required_columns):
                    flash('CSV must contain "name", "course", and "email" columns', 'danger')
                    return redirect(url_for('main.generate_certificates'))
                
                template = Template.query.filter_by(id=template_id, admin_id=user_id).first()
                if not template:
                    flash('Template not found', 'danger')
                    return redirect(url_for('main.generate_certificates'))
                
                # Get app config
                from flask import current_app
                config = current_app.config
                
                # Generate certificates
                generator = CertificateGenerator(template.background_path, config, field_config=template.field_configuration)
                generated_count = 0
                
                for index, row in df.iterrows():
                    recipient_name = row['name'].strip()
                    course_name = row['course'].strip()
                    student_email = row['email'].strip().lower()
                    
                    if not recipient_name or not course_name or not student_email:
                        continue

                    student = Student.query.filter_by(email=student_email).first()
                    if not student:
                        # Auto-create the student so bulk generation works smoothly
                        import uuid
                        username_base = student_email.split('@')[0]
                        unique_username = f"{username_base}_{str(uuid.uuid4())[:8]}"
                        student = Student(username=unique_username, email=student_email, is_active=True)
                        student.set_password('welcome123')
                        db.session.add(student)
                        db.session.flush()
                    
                    # Create certificate
                    cert_filename = f"cert_{int(datetime.now().timestamp() * 1000)}_{index}.pdf"
                    cert_path = os.path.join(config['CERTIFICATE_FOLDER'], cert_filename)
                    
                    # Create Certificate object first to get UID
                    cert = Certificate(
                        admin_id=user_id,
                        template_id=template.id,
                        student_id=student.id,
                        recipient_name=recipient_name,
                        student_email=student.email,
                        course_name=course_name,
                        pdf_path=cert_filename,
                        certificate_data={
                            'name': recipient_name,
                            'course': course_name,
                            'email': student.email,
                        }
                    )
                    db.session.add(cert)
                    db.session.flush()  # Get the certificate_uid

                    # QR will be generated with filename: qr_<certificate_uid>.png
                    cert.qr_code_path = f"/certificates/qr_{cert.certificate_uid}.png"
                    
                    generator.create_certificate_pdf(
                        recipient_name=recipient_name,
                        course_name=course_name,
                        issue_date=datetime.now(),
                        certificate_uid=cert.certificate_uid,
                        output_path=cert_path
                    )
                    
                    generated_count += 1
                
                db.session.commit()
                flash(f'Successfully generated {generated_count} certificates!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing CSV: {str(e)}', 'danger')
        else:
            flash('Only CSV files are allowed', 'danger')
    
    return render_template('generator.html', templates=templates)

@main_bp.route('/certificates/list')
@admin_required
def list_certificates():
    """List user's certificates"""
    user_id = session.get('user_id')
    page = request.args.get('page', 1, type=int)
    
    certificates = Certificate.query.filter_by(admin_id=user_id).paginate(page=page, per_page=20)
    
    return render_template('certificates_list.html', certificates=certificates)

@main_bp.route('/certificates/download/<int:cert_id>')
@login_required
def download_certificate(cert_id):
    """Download certificate PDF"""
    user_id = session.get('user_id')
    user_role = session.get('role')

    if user_role == 'admin':
        certificate = Certificate.query.filter_by(id=cert_id, admin_id=user_id).first()
    else:
        # Students can only download certificates assigned to them
        certificate = Certificate.query.filter_by(id=cert_id, student_id=user_id).first()

    if not certificate:
        flash('Certificate not found or access denied', 'danger')
        if user_role == 'admin':
            return redirect(url_for('main.list_certificates'))
        return redirect(url_for('main.student_dashboard'))

    cert_path = os.path.join(os.path.dirname(__file__), '..', 'certificates', certificate.pdf_path)

    if not os.path.exists(cert_path):
        flash('Certificate file not found', 'danger')
        if user_role == 'admin':
            return redirect(url_for('main.list_certificates'))
        return redirect(url_for('main.student_dashboard'))

    return send_file(cert_path, as_attachment=True, download_name=f'certificate_{certificate.certificate_uid}.pdf')

@main_bp.route('/certificates/<path:filename>')
def serve_certificate(filename):
    """Serve certificate files"""
    cert_path = os.path.join(os.path.dirname(__file__), '..', 'certificates', filename)
    if os.path.exists(cert_path):
        return send_file(cert_path)
    else:
        return "Certificate not found", 404

@main_bp.route('/statistics')
@admin_required
def statistics():
    """View statistics"""
    user_id = session.get('user_id')
    
    total_templates = Template.query.filter_by(admin_id=user_id, is_active=True).count()
    total_certificates = Certificate.query.filter_by(admin_id=user_id).count()
    total_verifications = sum([cert.verification_count for cert in Certificate.query.filter_by(admin_id=user_id).all()])
    
    return render_template('statistics.html',
                         total_templates=total_templates,
                         total_certificates=total_certificates,
                         total_verifications=total_verifications)
