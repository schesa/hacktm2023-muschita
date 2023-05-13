import os
import boto3
from botocore.exceptions import ProfileNotFound


def get_aws_credentials(profile_name):
    try:
        # Set the AWS_SHARED_CREDENTIALS_FILE environment variable
        #os.environ['AWS_SHARED_CREDENTIALS_FILE'] = '/root/.aws/credentials'
        print(f"Get AWS credentials for profile:{profile_name}")
        session = boto3.Session(profile_name="muskia")
        credentials = session.get_credentials()

        if credentials is None:
            return None

        aws_access_key_id = credentials.access_key
        aws_secret_access_key = credentials.secret_key
        aws_region = session.region_name

        return aws_access_key_id, aws_secret_access_key, aws_region
    except ProfileNotFound:
        return None


def upload_file_to_s3(file_path, file_name, file_directory, profile_name):
    credentials = get_aws_credentials(profile_name)

    if credentials is None:
        return False

    aws_access_key_id, aws_secret_access_key, aws_region = credentials

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

    S3_BUCKET_NAME = 'muskiatm'

    # Upload the file to the new directory in S3 bucket
    s3_key = f"{file_directory}/{file_name}"
    s3.upload_file(file_path, S3_BUCKET_NAME, s3_key)

    # Render the uploaded image and its details
    image_url = f"https://{S3_BUCKET_NAME}.s3.{aws_region}.amazonaws.com/{file_directory}/{file_name}"

    return image_url

def list_s3_directories(bucket_name, prefix):
    s3 = boto3.client('s3')
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')

    if 'CommonPrefixes' in response:
        directories = [common_prefix['Prefix'] for common_prefix in response['CommonPrefixes']]
        return directories
    else:
        return []

def get_last_upload_number(profile_name):
    credentials = get_aws_credentials(profile_name)

    if credentials is None:
        return 0

    aws_access_key_id, aws_secret_access_key, aws_region = credentials

    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=aws_region)

    S3_BUCKET_NAME = 'muskiatm'

    # Retrieve the list of objects in the S3 directory
    #response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME)
    directories = list_s3_directories(S3_BUCKET_NAME, '')

    last_number = 0
    for directory in directories:
        directory_name = os.path.basename(os.path.normpath(directory))
        try:
           file_number = int(directory_name.split('_')[1])
           last_number = max(last_number, file_number)
        except (IndexError, ValueError):
           continue

    return last_number

