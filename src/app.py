import logging
import os
import re
import configparser
from flask import Flask, render_template, request, redirect, url_for
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import urllib.parse
import time
import shutil

from utils import aws

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = "/uploads"
app.config['AWS_PROFILE'] = "muskia"

# Configure the logger
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Retrieve the uploaded file
        file = request.files['file']

        # Check if a file is selected
        if file.filename == '':
            return render_template('index.html', error_message='No file selected.')

        if not os.path.exists(app.config['UPLOAD_FOLDER']):
           app.config['UPLOAD_FOLDER']="../uploads"

        last_number = aws.get_last_upload_number(app.config['AWS_PROFILE'])
        print(f'Last upload number: {last_number}')
        number=last_number+1
        extension = get_file_extension(file.filename)
        new_name=f'upload_{number}.{extension}'
        new_directory=f'work_{number}'
        processed_directory=f'{new_directory}/processed_{number}'

        if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], new_directory)):
           os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], new_directory))

        # Save the uploaded file to the upload folder
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_directory, new_name)

        processed_directory = os.path.join(app.config['UPLOAD_FOLDER'], processed_directory)
        processed_picture_name = f"result.{extension}"

        print(f"Saving locally in {file_path}")
        file.save(file_path)

        file_size = os.path.getsize(file_path)
        file_format = file.content_type


        try:
            # Upload the file to S3
            image_url = aws.upload_file_to_s3(file_path,new_name,new_directory,app.config['AWS_PROFILE'])

            # Redirect to the result page with the uploaded image details
            return redirect(url_for('image_details', filename=new_name, size=file_size, format=file_format, work_unit=new_directory,
                                    s3_image_url=urllib.parse.quote(image_url),
                                    processed_directory=urllib.parse.quote(processed_directory),
                                    processed_picture_name=processed_picture_name))
        except (BotoCoreError, ClientError) as e:
            logging.error(e.response['Error']['Message'])
            return render_template('error.html', error_message="An error occurred while uploading the file.")

    return render_template('index.html')


@app.route('/image_details')
def image_details():
    filename = request.args.get('filename')
    size = request.args.get('size')
    file_format = request.args.get('format')
    work_unit = request.args.get('work_unit')
    decoded_image_url = urllib.parse.unquote(request.args.get('s3_image_url'))
    processed_directory = urllib.parse.unquote(request.args.get('processed_directory'))
    processed_picture_name = request.args.get('processed_picture_name')
    processed_picture_path = f"{processed_directory}/{processed_picture_name}"
    new_processed_picture_path = f"static/processed_{work_unit}/{processed_picture_name}"

    print(f"Waiting for {processed_picture_path}, to move it to {new_processed_picture_path}")
    if check_file(processed_picture_path,20):
        print(f"{processed_picture_path} arrived, copying to static")
        copy_directory(processed_directory, f"src/static/processed_{work_unit}")


    return render_template('image-details.html', filename=filename, size=size, work_unit=work_unit, format=file_format,
                           s3_image_url=decoded_image_url, processed_picture_path=new_processed_picture_path)

@app.route('/avatar')
def avatar():
    text = urllib.parse.unquote(request.args.get('text'))

    return render_template('avatar.html', text=text)


def get_file_extension(filename):
    pattern = r'\.(\w+)$'
    match = re.search(pattern, filename)
    if match:
        return match.group(1)
    else:
        return None

def print_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
            print(content)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except IOError:
        print(f"An error occurred while reading the file '{file_path}'.")

def check_file(path, max_attempts=30):
    attempts = 0
    while attempts < max_attempts:
        try:
            if os.path.isfile(path):
                print("File found!")
                return True
            else:
                print("File not found, waiting for 1 second...")
                time.sleep(1)
                attempts += 1
        except Exception as e:
            print(f"An error occurred: {e}")
            return False
    print("Giving up after 30 attempts.")
    return False


def copy_directory(src_dir, dst_dir):
    try:
        shutil.copytree(src_dir, dst_dir)
        print(f"Directory {src_dir} copied to {dst_dir}.")
    except Exception as e:
        print(f"An error occurred while copying the directory: {e}")


if __name__ == '__main__':
    #print_file_content("/root/.aws/credentials")
    app.run(host='0.0.0.0', port=5002)