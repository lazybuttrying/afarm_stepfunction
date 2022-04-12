import json
from datetime import datetime as dt
import csv
from requests import request
from dotenv import load_dotenv
import shutil
import subprocess
import os
import shutil
import boto3

root_path = "/tmp/"
load_dotenv()
hasura_key = os.environ.get("HASURA_KEY")
s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")

url = "https://better-rat-41.hasura.app/v1/graphql"
payload_getid = "{\"query\":\"query MyQuery {\\n  afarm_grape_aggregate(where: {quality_id: {_eq: %s}}) {\\n    aggregate {\\n      max {\\n        grape_id\\n      }\\n    }\\n  }\\n}\\n\",\"variables\":{}}"
headers = {
    "Content-Type":"application/json",
    "x-hasura-admin-secret": hasura_key
}

client_s3 = boto3.client( 's3',
        aws_access_key_id = s3_access_key,
        aws_secret_access_key = s3_secret_key
)
resource_s3 = boto3.resource( 's3', 
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

bucket = resource_s3.Bucket(bucket_name)

def upload_file(file, key):
    try:
        client_s3.upload_file(file, bucket_name, key)
    except Exception as e:
        print(f"Another Error => {e}")


def lambda_handler(event, context):
    quality_id = event["quality_id"]
    skip_frame = event["skip_frame"] if "skip_frame" in event else 30

    os.makedirs('/tmp/inference/crops/', exist_ok = True)
    os.makedirs('/tmp/inference/results/', exist_ok = True)
    src_path = '/tmp/src/'
    dest_path = '/tmp/inference/crops/'+str(quality_id)+"/"
    os.makedirs(src_path, exist_ok = True)
    os.makedirs(dest_path, exist_ok = True)
    print(os.listdir('/tmp/inference/'))
    print(os.listdir('/tmp/inference/crops'))

    # download images
    src_s3 = "grape_before/"+str(quality_id)+".mp4"
    bucket.download_file(src_s3, src_path+str(quality_id)+".mp4")
    print(os.listdir('/tmp/src/'))
    

    args = ['python3.9', 'track.py',
     '--yolo_weights', './yolov5/run22_best_yolov5.pt',
     '--source', src_path+str(quality_id)+".mp4", 
     '--quality_id', str(quality_id),
     '--skip_frame', str(skip_frame),
     '--save-txt', '--save-crop']
    test = subprocess.run(args, capture_output=True)
    print("Result: ", test.stdout)
    print("Error: ", test.stderr)
    print(os.listdir('/tmp/inference/crops'))
    print(os.listdir('/tmp/inference/crops/'+str(quality_id)))

    # get start poing of grape_id
    response = request("POST", url, headers=headers, 
                 data = payload_getid % (quality_id)).json()
    grape_id = response["data"]["afarm_grape_aggregate"]["aggregate"]["max"]["grape_id"]
    if grape_id is None:
        grape_id = 0
    print(grape_id, response)

    #result_csv = csv.reader(open(root_path+'inference/deepsort_result.csv', 'r'))
    #while (len(os.listdir(src_path)) > len(os.listdir(dest_path))):
    #    pass # wait until all result file c
    
    # for row in result_csv:
    #     if (row[0] == 'frame'):
    #         continue

    for f in os.listdir(root_path+'inference/crops/'+str(quality_id)+'/'):
        upload_file(root_path+'inference/crops/'+str(quality_id)+'/'+f, 'grape_before/'+str(quality_id)+'/'+f)


    return {
        "statusCode": 200,
        "quality_id": quality_id,
        "grape_id": grape_id,
        "body": json.dumps(
            {
               "quality_id" : quality_id,  
            }
        ),
    }

if __name__ == "__main__":
    x = lambda_handler({"quality_id":90},1)
    print(x)