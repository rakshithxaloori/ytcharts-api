import boto3

from botocore.exceptions import ClientError

from django.conf import settings


def create_presigned_s3_post(file_size, file_path):
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    FILE_TYPE = "image/png"
    URL_EXPIRY_SECS = 3600  # 1 hour

    fields = {
        "Content-Type": FILE_TYPE,
    }
    conditions = [
        ["content-length-range", file_size - 10, file_size + 10],
        {"content-type": FILE_TYPE},
    ]

    try:
        response = s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=file_path,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=URL_EXPIRY_SECS,
        )
        return response
    except ClientError as e:
        print(e)
        return None
