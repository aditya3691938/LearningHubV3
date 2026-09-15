import os
import time
import socket
import qrcode
from flask import current_app, request, has_request_context

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def generate_class_qr(class_id, base_url=None):
    """
    Generates a QR code image for a Live Class.
    QR payload: <base_url>/learner/login?classId=xxxxx
    Saves image in static/qr_codes directory.
    Returns relative static URL with cache buster parameter.
    """
    if not base_url:
        base_url = os.environ.get('PUBLIC_URL') or os.environ.get('BASE_URL')
        if not base_url and current_app:
            base_url = current_app.config.get('PUBLIC_URL') or current_app.config.get('BASE_URL')
        if not base_url and has_request_context():
            base_url = request.host_url
        if not base_url:
            base_url = "http://localhost:5000"

    # If running locally without explicit PUBLIC_URL env, replace localhost/127.0.0.1 with local LAN IP
    # so mobile phones scanning the QR code can reach the local server over Wi-Fi
    is_env_public = bool(os.environ.get('PUBLIC_URL') or os.environ.get('BASE_URL'))
    if not is_env_public:
        if 'localhost' in base_url.lower() or '127.0.0.1' in base_url:
            local_ip = get_local_ip()
            if local_ip and local_ip != '127.0.0.1':
                base_url = base_url.replace('localhost', local_ip).replace('127.0.0.1', local_ip)

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

    timestamp = int(time.time())
    return f"/static/qr_codes/{filename}?v={timestamp}"
