import json
import boto3
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

def get_labels(bucket, key):
    rekognition = boto3.client("rekognition", region_name="us-east-1")
    print(bucket)
    print(key)
    response = rekognition.detect_labels(
        Image={
            "S3Object":
            {"Bucket": bucket,
             "Name": key}
        },
        MinConfidence=90, MaxLabels=20)
    # print(response)
    
    labels = [x['Name'] for x in response["Labels"]]
    metadata = get_metadata(bucket, key)
    if bool(metadata) and len(metadata) > 0:
        metadata = metadata['customlabels'].split(',')
        labels = labels + metadata

    json_data = {
        "object_key": key,
        "bucket": bucket,
        "createdTimestamp": datetime.now().isoformat(),
        "labels": labels
    }
    return json_data
    

def get_metadata(bucket, key):
    s3 = boto3.client("s3", region_name="us-east-1")
    response = s3.head_object(Bucket=bucket, Key=key)
    # print(response)
    return response["Metadata"]
    

def lambda_handler(event, context):
    print(event)
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    # bucket = 'ccphotoalbum'
    # key = 'bmw_m_wall.jpg'
    print(bucket)
    print(key)
    labels_json = get_labels(bucket, key)
    
    auth = HTTPBasicAuth(
        "ccphotoalbum", "Ccphotoalbum@2024")
    headers: dict = {"Content-Type": "application/json"}
    url = "https://search-ccphotoalbum-okobqcqxaiuu5do2ujtwm3o6iu.aos.us-east-1.on.aws" + '/photos/' + 'photo/'+ datetime.now().isoformat() + labels_json['object_key']
    response = requests.post(url, json=labels_json, headers=headers, auth=auth)
    print(response)
    # r.raise_for_status()
    # logger.debug(
    #     "{} returned from POST {} - json: {}".format(r.status_code, OS_URL, payload))
    
    return {
        "statusCode": 200,
        "body": json.dumps(response.json())
    }
