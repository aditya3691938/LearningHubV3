from flask import Blueprint, render_template, request, redirect, url_for, flash, session, send_file, current_app
import os
from datetime import datetime
from app.models import db
from app.models.certificate import Certificate
from app.models.user import Learner
from app.models.course import Course
from app.services.pdf_service import generate_certificate_pdf

from app.utils.decorators import admin_required

certificates_bp = Blueprint('certificates', __name__)

@certificates_bp.route('/')
@admin_required
def list_certificates():

    search_query = request.args.get('search', '').strip()
    query = Certificate.query.join(Learner).join(Course)

    if search_query:
        query = query.filter(
            (Certificate.certificate_id.ilike(f'%{search_query}%')) |
            (Learner.name.ilike(f'%{search_query}%')) |
            (Learner.global_id.ilike(f'%{search_query}%')) |
            (Course.name.ilike(f'%{search_query}%'))
        )

    certs = query.order_by(Certificate.issue_date.desc()).all()
    return render_template('certificates/list.html', certificates=certs, search_query=search_query)


@certificates_bp.route('/my_certificates')
def my_certificates():
    learner_id = session.get('learner_id')
    if not learner_id:
        flash("Please log in to view your certificates.", "info")
        return redirect(url_for('auth.learner_login'))
        
    _ensure_external_cert_columns()
    learner = Learner.query.get_or_404(learner_id)
    certificates = Certificate.query.filter_by(learner_id=learner.id).order_by(Certificate.issue_date.desc()).all()
    
    from app.models.external_certificate import ExternalCertificate
    external_certificates = ExternalCertificate.query.filter_by(learner_id=learner.id).order_by(ExternalCertificate.date_earned.desc()).all()
    
    return render_template('learner_portal/certificates.html', learner=learner, certificates=certificates, external_certificates=external_certificates)


def _ensure_external_cert_columns():
    from app.models import db
    from sqlalchemy import text
    try:
        db.session.execute(text("ALTER TABLE external_certificates ADD COLUMN expiry_date DATE"))
        db.session.commit()
    except Exception:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE external_certificates ADD COLUMN ocr_validated BOOLEAN DEFAULT 1"))
        db.session.commit()
    except Exception:
        db.session.rollback()

@certificates_bp.route('/upload_external', methods=['POST'])
def upload_external():
    learner_id = session.get('learner_id')
    if not learner_id:
        flash("Please log in to upload certificates.", "danger")
        return redirect(url_for('auth.learner_login'))
        
    _ensure_external_cert_columns()
    learner = Learner.query.get(learner_id)
    learner_name = learner.name if learner else None

    course_name = request.form.get('course_name', '').strip()
    issuing_org = request.form.get('issuing_org', '').strip()
    date_earned_str = request.form.get('date_earned', '').strip()
    expiry_date_str = request.form.get('expiry_date', '').strip()
    skills = request.form.get('skills', '').strip()
    file = request.files.get('certificate_file')
    
    if not course_name or not issuing_org or not date_earned_str:
        flash("Certification Name, Issuing Organization, and Date Earned are required.", "danger")
        return redirect(url_for('certificates.my_certificates'))
        
    if not file or not file.filename:
        flash("Please attach your certificate PDF file for backend OCR validation.", "danger")
        return redirect(url_for('certificates.my_certificates'))

    ext = os.path.splitext(file.filename)[1].lower()
    if ext != '.pdf':
        flash("Please attach a valid PDF file (.pdf) for OCR verification.", "danger")
        return redirect(url_for('certificates.my_certificates'))

    # Parse dates
    try:
        date_earned = datetime.strptime(date_earned_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid Date Earned format. Use YYYY-MM-DD.", "danger")
        return redirect(url_for('certificates.my_certificates'))

    expiry_date = None
    if expiry_date_str:
        try:
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    # Reset stream pointer
    file.seek(0)

    # Run Backend OCR Text Validation
    from app.services.ocr_service import validate_certificate_pdf
    is_valid_ocr, discrepancy_msg, extracted_text = validate_certificate_pdf(
        file, 
        course_name=course_name, 
        issuing_org=issuing_org, 
        learner_name=learner_name, 
        date_earned=date_earned
    )

    if not is_valid_ocr:
        flash(f"{discrepancy_msg}", "danger")
        return redirect(url_for('certificates.my_certificates'))

    # Upload PDF file to Local storage AND B2
    pdf_filename = None
    b2_cert_file = request.form.get('b2_uploaded_filename')
    if b2_cert_file:
        pdf_filename = b2_cert_file
    else:
        from werkzeug.utils import secure_filename
        import uuid
        pdf_filename = f"ext_cert_{uuid.uuid4().hex}{ext}"

        # 1. Guaranteed Local Save
        file.seek(0)
        upload_dir = os.path.abspath(os.path.join(current_app.root_path, '..', 'uploads', 'external_certs'))
        os.makedirs(upload_dir, exist_ok=True)
        local_path = os.path.join(upload_dir, pdf_filename)
        file.save(local_path)
        file.seek(0)

        # 2. Cloud B2 Upload Attempt
        try:
            from app.services.b2_service import upload_file_to_b2
            uploaded_name = upload_file_to_b2(file, pdf_filename, folder='external_certs', content_type=file.content_type)
            if uploaded_name:
                pdf_filename = uploaded_name
        except Exception as b2_err:
            print(f"B2 upload notice: {b2_err}")
        
    from app.models.external_certificate import ExternalCertificate
    ext_cert = ExternalCertificate(
        learner_id=learner_id,
        course_name=course_name,
        issuing_org=issuing_org,
        date_earned=date_earned,
        expiry_date=expiry_date,
        pdf_filename=pdf_filename,
        skills=skills,
        ocr_validated=True
    )
    db.session.add(ext_cert)
    
    if learner:
        learner.points += 100
        
    db.session.commit()
    
    flash("External Certificate successfully validated via Backend OCR and accepted! Earned 100 profile points.", "success")
    return redirect(url_for('certificates.my_certificates'))

@certificates_bp.route('/download/<cert_id_str>')
def download_certificate(cert_id_str):
    cert = Certificate.query.filter_by(certificate_id=cert_id_str).first_or_404()
    learner = cert.learner
    course = cert.course

    cert_filename = f"cert_{cert.certificate_id}.pdf"
    pdf_dir = os.path.join(certificates_bp.root_path, '..', '..', 'uploads', 'certificates')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, cert_filename)

    if not os.path.exists(pdf_path):
        date_str = cert.issue_date.strftime('%d-%b-%Y')
        generate_certificate_pdf(learner.name, course.name, date_str, cert.certificate_id, pdf_path)

    return send_file(pdf_path, as_attachment=True, download_name=f"Certificate_{cert.certificate_id}.pdf")


@certificates_bp.route('/external/<int:cert_id>')
def serve_external_certificate(cert_id):
    """
    Serves or redirects uploaded external certificates.
    Checks local server disk first, then falls back to B2 presigned URLs.
    """
    from app.models.external_certificate import ExternalCertificate
    from app.services.b2_service import get_b2_url
    from flask import send_file, redirect, abort, current_app
    import os

    cert = ExternalCertificate.query.get_or_404(cert_id)
    if not cert.pdf_filename:
        abort(404, description="No certificate file associated with this record.")

    raw_filename = str(cert.pdf_filename).strip()

    # 1. Direct HTTP / HTTPS URL
    if raw_filename.startswith('http://') or raw_filename.startswith('https://'):
        return redirect(raw_filename)

    clean_name = os.path.basename(raw_filename)
    clean_rel = raw_filename.lstrip('/\\')

    # 2. Local filesystem candidates (CHECK LOCAL SERVER FIRST!)
    candidates = [
        os.path.abspath(os.path.join(current_app.root_path, '..', 'uploads', 'external_certs', clean_name)),
        os.path.join(current_app.root_path, 'static', 'uploads', 'external_certs', clean_name),
        os.path.join(current_app.root_path, 'static', 'uploads', clean_name),
        os.path.abspath(os.path.join(current_app.root_path, '..', 'uploads', clean_name)),
        os.path.abspath(os.path.join(current_app.root_path, '..', clean_rel)),
    ]

    for c_path in candidates:
        norm_path = os.path.normpath(c_path)
        if os.path.isfile(norm_path) and os.path.getsize(norm_path) > 0:
            resp = send_file(norm_path, mimetype='application/pdf', as_attachment=False, conditional=True)
            resp.headers['Accept-Ranges'] = 'bytes'
            return resp

    # 3. Backblaze B2 presigned URL fallback if not on local disk
    b2_url = get_b2_url(raw_filename, folder='external_certs') or get_b2_url(raw_filename)
    if b2_url and (b2_url.startswith('http://') or b2_url.startswith('https://')):
        return redirect(b2_url)

    # 4. Fallback redirect if B2 returned relative static path
    if b2_url and b2_url.startswith('/'):
        return redirect(b2_url)

    abort(404, description="External certificate PDF file could not be located on local server or cloud.")

    abort(404, description="External certificate PDF file could not be located on cloud or local server.")

