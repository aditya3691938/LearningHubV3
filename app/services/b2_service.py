import os
import boto3
from botocore.exceptions import ClientError
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
        aws_secret_access_key=application_key
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

def get_b2_url(filename, folder=''):
    """
    Generates the public Cloud URL for a file in the B2 bucket.
    """
    endpoint = os.environ.get('B2_ENDPOINT_URL') or os.environ.get('S3_ENDPOINT_URL')
    bucket = os.environ.get('B2_BUCKET_NAME') or os.environ.get('S3_BUCKET')
    if not endpoint or not bucket or not filename:
        return None

    endpoint = endpoint.rstrip('/')
    if folder:
        return f"{endpoint}/{bucket}/{folder}/{filename}"
    return f"{endpoint}/{bucket}/{filename}"

