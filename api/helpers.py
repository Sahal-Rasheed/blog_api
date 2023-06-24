import boto3
from django.conf import settings


s3 = boto3.client(
    's3', 
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)

def upload_image_to_s3(image_file, image_key):
    s3.upload_fileobj(image_file, settings.AWS_STORAGE_BUCKET_NAME, image_key)

def delete_image_from_s3(image_key):
    s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=image_key)
