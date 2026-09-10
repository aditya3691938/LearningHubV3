import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
from werkzeug.utils import secure_filename

def get_b2_client():
    endpoint = os.environ.get('B2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL')
    key_id = os.environ.get('B2_KEY_ID') or os.environ.get('S3_ACCESS_KEY')
    application_key = os.environ.get('B2_APPLICATION_KEY') or os.environ.get('S3_SECRET_KEY')

    if not endpoint or not key_id or not application_key:
        return None

    return boto3.client(
        service_name='s3',
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=application_key,
        config=Config(signature_version='s3v4')
    )

def upload_file_to_b2(file_obj, filename, folder='', content_type=None):
    """
    Uploads a file to Backblaze B2 cloud storage and returns the secure filename.
    Also maintains a local copy in uploads/<folder>/ for server-side processing & fallback.
    """
    if not file_obj or not filename:
        return None

    secure_name = secure_filename(filename)
    if folder:
        key = f"{folder}/{secure_name}"
    else:
        key = secure_name

    # Always ensure local copy exists in uploads/<folder> for fallback & local tools
    base_upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
    target_dir = os.path.join(base_upload_dir, folder) if folder else base_upload_dir
    os.makedirs(target_dir, exist_ok=True)
    local_file_path = os.path.join(target_dir, secure_name)

    try:
        if hasattr(file_obj, 'seek'):
            file_obj.seek(0)
        
        if hasattr(file_obj, 'save'):
            file_obj.save(local_file_path)
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
        elif hasattr(file_obj, 'read'):
            content = file_obj.read()
            with open(local_file_path, 'wb') as f:
                f.write(content)
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)
    except Exception as e:
        print(f"Local file save notice: {e}")

    b2 = get_b2_client()
    bucket_name = os.environ.get('B2_BUCKET_NAME') or os.environ.get('S3_BUCKET')

    if b2 and bucket_name:
        extra_args = {}
        if content_type:
            extra_args['ContentType'] = content_type

        try:
            if hasattr(file_obj, 'seek'):
                file_obj.seek(0)

            b2.upload_fileobj(
                file_obj,
                bucket_name,
                key,
                ExtraArgs=extra_args
            )
            print(f"Successfully uploaded '{key}' to Backblaze B2 Cloud.")
        except Exception as e:
            print(f"B2 Upload Error for '{key}': {e}")
            if os.path.exists(local_file_path):
                try:
                    b2.upload_file(local_file_path, bucket_name, key, ExtraArgs=extra_args)
                    print(f"Successfully uploaded '{key}' to Backblaze B2 Cloud from local copy.")
                except Exception as e2:
                    print(f"B2 Direct File Upload Error: {e2}")

    return secure_name

def generate_presigned_upload_url(filename, folder='', content_type=None, expires_in=3600):
    """
    Generates a SigV4 presigned PUT URL allowing the client browser to upload a file directly to B2.
    """
    import uuid
    b2 = get_b2_client()
    bucket = os.environ.get('B2_BUCKET_NAME') or os.environ.get('S3_BUCKET')
    if not b2 or not bucket or not filename:
        return None

    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    short_id = uuid.uuid4().hex[:8]
    clean_name = secure_filename(name) or "file"
    unique_filename = f"{clean_name}_{short_id}{ext}"

    key = f"{folder}/{unique_filename}" if folder else unique_filename

    params = {'Bucket': bucket, 'Key': key}
    if content_type:
        params['ContentType'] = content_type

    try:
        url = b2.generate_presigned_url(
            'put_object',
            Params=params,
            ExpiresIn=expires_in
        )
        endpoint = os.environ.get('B2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL') or ''
        public_url = f"{endpoint.rstrip('/')}/{bucket}/{key}"
        return {
            'upload_url': url,
            'key': key,
            'filename': unique_filename,
            'public_url': public_url,
            'bucket': bucket
        }
    except Exception as e:
        print(f"Error generating B2 presigned upload URL: {e}")
        return None


def download_file_from_b2(filename, folder='', local_path=None):
    """
    Downloads a file from B2 to local_path on demand (e.g. SCORM zip extraction).
    """
    b2 = get_b2_client()
    bucket = os.environ.get('B2_BUCKET_NAME') or os.environ.get('S3_BUCKET')
    if not b2 or not bucket or not filename:
        return False

    key = f"{folder}/{filename}" if folder else filename
    if not local_path:
        base_upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads'))
        target_dir = os.path.join(base_upload_dir, folder) if folder else base_upload_dir
        os.makedirs(target_dir, exist_ok=True)
        local_path = os.path.join(target_dir, filename)
    else:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

    try:
        b2.download_file(bucket, key, local_path)
        print(f"Successfully downloaded '{key}' from B2 to '{local_path}'.")
        return True
    except Exception as e:
        print(f"B2 Download Error for '{key}': {e}")
        return False
def get_b2_url(filename, folder='', expires_in=86400):
    """
    Generates the Cloud URL for a file in the B2 bucket.
    If the bucket is Private or credentials are configured, generates a SigV4 presigned URL
    allowing direct browser playback/downloads without 'UnauthorizedAccess' errors.
    """
    endpoint = os.environ.get('B2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL')
    bucket = os.environ.get('B2_BUCKET_NAME') or os.environ.get('S3_BUCKET')
    if not endpoint or not bucket or not filename:
        return None

    key = f"{folder}/{filename}" if folder else filename
    b2 = get_b2_client()

    if b2:
        try:
            return b2.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': key},
                ExpiresIn=expires_in
            )
        except Exception as e:
            print(f"Presigned URL generation notice: {e}")

    endpoint = endpoint.rstrip('/')
    return f"{endpoint}/{bucket}/{key}"




