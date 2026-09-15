import os
import qrcode
from flask import current_app, request, has_request_context

def generate_class_qr(class_id, base_url=None):
    """
    Generates a QR code image for a Live Class.
    QR payload: <base_url>/learner/login?classId=xxxxx
    Saves image in static/qr_codes directory.
    Returns relative static URL.
    """
    if not base_url:
        base_url = os.environ.get('PUBLIC_URL') or os.environ.get('BASE_URL')
        if not base_url and current_app:
            base_url = current_app.config.get('PUBLIC_URL') or current_app.config.get('BASE_URL')
        if not base_url and has_request_context():
            base_url = request.host_url
        if not base_url:
            base_url = "http://localhost:5000"
    base_url = base_url.rstrip('/')
    target_url = f"{base_url}/learner/login?classId={class_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(target_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#003366", back_color="#FFFFFF")
    
    filename = f"qr_{class_id}.png"
    qr_dir = os.path.join(current_app.root_path, 'static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    file_path = os.path.join(qr_dir, filename)
    img.save(file_path)

    return f"/static/qr_codes/{filename}"
