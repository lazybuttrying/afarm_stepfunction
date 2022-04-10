import json
from datetime import datetime as dt
from collections import deque
import csv
from dotenv import load_dotenv
from requests import request
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



objs = "{quality_id: %s, grape_id: %s, berry: %s, sick_berry: %s, img: \\\"%s\\\"}," 
payload_objs ="{\"query\":\"mutation MyMutation {\\n  insert_afarm_grape(objects: [%s]) {\\n    returning {\\n      grape_id\\n    }\\n  }\\n}\\n\",\"variables\":{}}"
payload_getid = "{\"query\":\"query MyQuery {\\n  afarm_grape_aggregate(where: {quality_id: {_eq: %s}}) {\\n    aggregate {\\n      max {\\n        grape_id\\n      }\\n    }\\n  }\\n}\\n\",\"variables\":{}}"

#payload="{\"query\":\"mutation MyMutation {\\n  insert_afarm_grape_one(object: {quality_id: %s, grape_id: %s, img: \\\"%s\\\", berry: %s}) {\\n    grape_id\\n  }\\n}\\n\",\"variables\":{}}"
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

def prefix_exits(bucket, path):
    res = client_s3.list_objects_v2(Bucket=bucket, Prefix=path, MaxKeys=1)
    return 'Contents' in res


def upload_file(file, key):
    try:
        client_s3.upload_file(file, bucket_name, "public/result/"+key)
    except Exception as e:
        print(f"Another Error => {e}")


def lambda_handler(event, context):
    # mkdir image folders
    quality_id = event["quality_id"] 
    src_path = root_path+'img/'+str(quality_id)+"/"
    dest_path = root_path+'viz/'+str(quality_id)+"/"
    os.makedirs(root_path+'viz/results/', exist_ok = True)
    os.makedirs(src_path, exist_ok = True)
    os.makedirs(dest_path, exist_ok = True)

    # download images
    src_s3 = "grape_before/"+str(quality_id)+"/"
    path = deque()
    for obj in bucket.objects.filter(Prefix=src_s3):
        if obj.key[-1] != "/":
            fname = str(dt.now()).replace(" ","_")+obj.key.split("/")[-1]
            bucket.download_file(obj.key, src_path+fname)
            path.append(fname)
            
    args = ['python3.9', "/var/task/box/demo/demo.py", "--input"]
    for p in list(map(lambda x:src_path+x, list(path))):
        args.append(p)
    for x in [ "--code", str(quality_id), 
            "--output", dest_path,
        "--opts", "MODEL.DEVICE", "cpu",
        "MODEL.WEIGHTS", "/var/task/box/training_dir/BoxInst_MS_R_50_1x/model_final.pth"]:
        args.append(x)
    test = subprocess.run(args, capture_output=True)
    print(test)

    # get start poing of grape_id
    response = request("POST", url, headers=headers, 
                 data = payload_getid % (quality_id)).json()
    grape_id = response["data"]["afarm_grape_aggregate"]["aggregate"]["max"]["grape_id"]
    if grape_id is None:
        grape_id = 0
    print(grape_id, response)
    # get result
    result_csv = csv.reader(open(root_path+'viz/results/'+str(quality_id)+'.csv'))
    
    # check all images are saved
    while (len(os.listdir(src_path)) > len(os.listdir(dest_path))):
        pass # wait until all result image file created
    

    result = {"data":{}}
    payload_grapes = ""
    
    # upload result to s3 and prepare GraphQL payload
    while path:
        grape_id += 1
        p = path.popleft()
        berry = int(next(result_csv)[1])
        payload_grapes += objs % (quality_id, grape_id, berry, 0, p)
        result["data"][p]=int(berry)
        upload_file(dest_path+p, p)

     # save all the data
    response = request("POST", url, headers=headers, 
                 data = payload_objs % (payload_grapes)).json()
    print(response) 
# #     uvicorn.run(app, host="0.0.0.0", port=5000)
    # for p in path:
    #     grape_id += 1
    #     berry = int(next(result_csv)[1]) 
    #     response = request("POST", url, headers=headers, 
    #             data = payload % (quality_id, grape_id, p, berry)).json()
    #     print(response)
    #     while "errors" in response:
    #         grape_id += 1
    #         response = request("POST", url, headers=headers, 
    #             data = payload % (quality_id, grape_id, p, berry)).json()
    #         print(response)    
    #     result["data"][p]=int(berry)
    #shutil.rmtree(src_path)
    #shutil.rmtree(dest_path)

    return {
        "statusCode": 200,
        "quality_ud": quality_id,
        "body": json.dumps(
                result
                )                
            }


if __name__ == "__main__":
    x = lambda_handler({"quality_id":90},1)
    print(x)