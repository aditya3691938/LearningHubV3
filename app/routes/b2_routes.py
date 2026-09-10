from flask import Blueprint, request, jsonify, session
from app.services.b2_service import generate_presigned_upload_url
import os

b2_bp = Blueprint('b2', __name__)

@b2_bp.route('/api/b2/presigned-upload-url', methods=['POST'])
def get_presigned_upload_url():
    """
    API Endpoint called by client JS to obtain a Backblaze B2 SigV4 presigned PUT URL.
    This enables direct browser-to-B2 uploads without passing binary file data through Render.
    """
    if not session.get('admin_logged_in') and not session.get('learner_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json(silent=True) or request.form
    filename = data.get('filename')
    folder = data.get('folder', '')
    content_type = data.get('content_type')

    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    allowed_folders = ['thumbnails', 'materials', 'audio', 'scorm', 'profile_pics', 'dashboard', 'external_certs', 'general']
    if folder and folder not in allowed_folders:
        folder = 'general'

    b2_info = generate_presigned_upload_url(filename, folder=folder, content_type=content_type)
    if not b2_info:
        return jsonify({'error': 'Cloud storage credentials not configured or failed to generate presigned upload URL'}), 500

    return jsonify({
        'success': True,
        'upload_url': b2_info['upload_url'],
        'key': b2_info['key'],
        'filename': b2_info['filename'],
        'public_url': b2_info['public_url'],
        'folder': folder
    })
