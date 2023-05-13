import logging
import os
import configparser
from flask import Flask, render_template, request
import boto3
from botocore.exceptions import BotoCoreError, ClientError

app = Flask(__name__)

# Set the AWS profile name
aws_profile = "muskia"

# Configure the logger
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Retrieve the uploaded file
        file = request.files['file']

        # Retrieve the S3 bucket and region for the selected profile from the AWS credentials file
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.aws/credentials"))
        bucket_name = 'muskiatm'
        region = config.get(aws_profile, 'region')

        # Create the S3 client
        session = boto3.Session(profile_name=aws_profile)
        s3 = session.client('s3')

        # Enable debug logging for the S3 client
        s3.meta.events.register('before-sign.s3', lambda **kwargs: logging.debug('S3 Request: %s', kwargs))

        try:
            # Upload the file to S3
            s3.upload_fileobj(file, bucket_name, file.filename)

            # Render the uploaded image and its details
            image_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{file.filename}"
            image_details = {'Filename': file.filename, 'Size': file.content_length, 'Format': file.content_type}

            return render_template('index.html', image_url=image_url, image_details=image_details)
        except (BotoCoreError, ClientError) as e:
            logging.error(e.response['Error']['Message'])
            return render_template('error.html', error_message="An error occurred while uploading the file.")

    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5002)