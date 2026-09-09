import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

def get_b2_client():
    return boto3.client(
        service_name='s3',
        endpoint_url=os.environ.get('B2_ENDPOINT_URL'),
        aws_access_key_id=os.environ.get('B2_KEY_ID'),
        aws_secret_access_key=os.environ.get('B2_APPLICATION_KEY')
    )

def upload_file_to_b2(file_obj, filename, folder='', content_type=None):
    """
    Uploads a file to Backblaze B2 and returns the filename.
    """
    b2 = get_b2_client()
    bucket_name = os.environ.get('B2_BUCKET_NAME')
    
    secure_name = secure_filename(filename)
    if folder:
        key = f"{folder}/{secure_name}"
    else:
        key = secure_name
        
    extra_args = {}
    if content_type:
        extra_args['ContentType'] = content_type
        
    try:
        b2.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs=extra_args
        )
        return secure_name
    except ClientError as e:
        print(f"B2 Upload Error: {e}")
        return None

def get_b2_url(filename, folder=''):
    """
    Generates the public URL for a file in the B2 bucket.
    """
    endpoint = os.environ.get('B2_ENDPOINT_URL')
    bucket = os.environ.get('B2_BUCKET_NAME')
    if folder:
        return f"{endpoint}/{bucket}/{folder}/{filename}"
    return f"{endpoint}/{bucket}/{filename}"
