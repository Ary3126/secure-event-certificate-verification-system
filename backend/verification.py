from flask import Blueprint, render_template, request, jsonify
from .models import Certificate, VerificationLog, db

verify_bp = Blueprint('verify', __name__, url_prefix='/verify')

@verify_bp.route('/')
def verify_page():
    """Public verification page"""
    return render_template('verify.html')

@verify_bp.route('/search', methods=['POST'])
def search_certificate():
    """Search for certificate by ID or UID"""
    data = request.get_json()
    certificate_id = data.get('certificate_id', '').strip()
    
    if not certificate_id:
        return jsonify({'status': 'error', 'message': 'Certificate ID is required'}), 400
    
    # Search by certificate UID
    certificate = Certificate.query.filter_by(certificate_uid=certificate_id).first()
    
    if not certificate:
        return jsonify({'status': 'error', 'message': 'Certificate not found'}), 404
    
    # Log verification
    try:
        log = VerificationLog(
            certificate_id=certificate.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            verification_method='search'
        )
        db.session.add(log)
        certificate.increment_verification()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    # Return certificate details
    return jsonify({
        'status': 'success',
        'certificate': {
            'uid': certificate.certificate_uid,
            'recipient_name': certificate.recipient_name,
            'course_name': certificate.course_name,
            'issue_date': certificate.issue_date.strftime('%B %d, %Y'),
            'pdf_path': certificate.pdf_path,
            'verification_count': certificate.verification_count
        }
    }), 200

@verify_bp.route('/qr/<certificate_uid>')
def verify_qr(certificate_uid):
    """Verify certificate from QR code"""
    certificate = Certificate.query.filter_by(certificate_uid=certificate_uid).first()
    
    if not certificate:
        return render_template('certificate_not_found.html'), 404
    
    # Log verification
    try:
        log = VerificationLog(
            certificate_id=certificate.id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            verification_method='qr'
        )
        db.session.add(log)
        certificate.increment_verification()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    
    return render_template('certificate_details.html', certificate=certificate)

@verify_bp.route('/api/certificate/<certificate_uid>')
def get_certificate_api(certificate_uid):
    """API endpoint to get certificate details"""
    certificate = Certificate.query.filter_by(certificate_uid=certificate_uid).first()
    
    if not certificate:
        return jsonify({'status': 'error', 'message': 'Certificate not found'}), 404
    
    return jsonify({
        'status': 'success',
        'certificate': {
            'uid': certificate.certificate_uid,
            'recipient_name': certificate.recipient_name,
            'course_name': certificate.course_name,
            'issue_date': certificate.issue_date.strftime('%B %d, %Y'),
            'expiry_date': certificate.expiry_date.strftime('%B %d, %Y') if certificate.expiry_date else 'N/A',
            'verification_count': certificate.verification_count,
            'pdf_url': f'/certificates/{certificate.pdf_path}'
        }
    }), 200
