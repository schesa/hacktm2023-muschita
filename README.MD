# MUSKIA project

## Overview
This project contains scripts and queries used by the MUSKIA sidekicker

## Setup

* **Install python dependencies from *requirements.txt***
```bash
 pip3.9 install -r requirements.txt
 python3.9 src/app.py
```
http://127.0.0.1:5002git init

## Services
Functionalities provided by the script arguments. These are mutually exclusive per script execution.
* **--upload image** Uploads an immage


## Run locally as docker:
docker build -t image-uploader .
docker run -p 5002:5000 -it image-uploader



###test call the container lambda handler (needs test_local to work with local profile)
`curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations"      -d '{"test_local": "value"}'`
##this is how an S3 trigger event looks like:
`"{'Records': [{'eventVersion': '2.1', 'eventSource': 'aws:s3', 'awsRegion': 'eu-central-1', 'eventTime': '2021-12-03T09:47:47.080Z', 'eventName': 'ObjectCreated:Put', 'userIdentity': {'principalId': 'A281W46RU00LXE'}, 'requestParameters': {'sourceIPAddress': '82.77.146.71'}, 'responseElements': {'x-amz-request-id': 'NJV4AEQM1W228REE', 'x-amz-id-2': '+OCDzDRZWnhoq/kTsHFxhr3T+69g+6O1LhTm7iN7ycPcd9nZqtpUXzzdLsehnng47ElNLh8ivvj6vSAKT9OGvHiAIkhc2z11'}, 's3': {'s3SchemaVersion': '1.0', 'configurationId': 'df6a4447-5dd2-4fa0-8be6-96f5a209eed5', 'bucket': {'name': 'devintent', 'ownerIdentity': {'principalId': 'A281W46RU00LXE'}, 'arn': 'arn:aws:s3:::devintent'}, 'object': {'key': 'new/requirements.txt', 'size': 474, 'eTag': 'f9b811946ead32e99787d7fc88b54f24', 'sequencer': '0061A9E7C2D5510122'}}}]}"`
