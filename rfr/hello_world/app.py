import json
from datetime import datetime as dt
from csv import reader
from dotenv import load_dotenv
from requests import request
from subprocess import Popen, run, PIPE
import os
from boto3 import client, resource
import logging
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

logging.basicConfig(
    format='%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)s) %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

root_path = "/tmp/"
load_dotenv()
hasura_key = os.environ.get("HASURA_KEY")
s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")


url = "https://better-rat-41.hasura.app/v1/graphql"

objs = "{quality_id: %s, grape_id: %s, berry: %s, sick_berry: %s, img: \\\"%s\\\"}," 
payload_objs ="{\"query\":\"mutation MyMutation {\\n  insert_afarm_grape(objects: [%s]) {\\n    returning {\\n      grape_id\\n    }\\n  }\\n}\\n\",\"variables\":{}}"

#payload="{\"query\":\"mutation MyMutation {\\n  insert_afarm_grape_one(object: {quality_id: %s, grape_id: %s, img: \\\"%s\\\", berry: %s}) {\\n    grape_id\\n  }\\n}\\n\",\"variables\":{}}"
headers = {
    "Content-Type":"application/json",
    "x-hasura-admin-secret": hasura_key
}

client_s3 = client( 's3',
        aws_access_key_id = s3_access_key,
        aws_secret_access_key = s3_secret_key
)

resource_s3 = resource( 's3', 
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

bucket = resource_s3.Bucket(bucket_name)


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)
    # mkdir image folders
    quality_id = event["quality_id"]
    grape_id_dict = json.loads(event["grape_id"]) # {start, end, count}
    src_path = root_path+'img/'+str(quality_id)+"/"
    dest_path = root_path+'viz/'+str(quality_id)+"/"
    mask_path = root_path+'regression_data/masks/'+str(quality_id)+"/"
    csv_path = "/tmp/viz/results/"+str(quality_id)+".csv"
     
    os.makedirs(root_path+'viz/results/', exist_ok = True)
    os.makedirs(src_path, exist_ok = True)
    os.makedirs(dest_path, exist_ok = True)
    os.makedirs(mask_path, exist_ok = True)

    # download csv
    bucket.download_file("mask/"+str(quality_id)+".csv", csv_path)
    
    # download masks
    Popen(["python3.9", "./download/download_masks.py", 
        "--mask_path", mask_path,
        "--quality_id", str(quality_id)],
           stdout=PIPE)

    # download images
    src_s3 = "grape_before/"+str(quality_id)+"/"
    result_csv = reader(open(root_path+'viz/results/'+str(quality_id)+'.csv'))
    for row in result_csv:
        fname = row[0]
        bucket.download_file(src_s3+fname, src_path+fname) 


    args = ["python3.9", "/var/task/grape_rfr/rfr.py", "--inference",
        "--regressor-path", "/var/task/grape_rfr/regressor_model.pkl",
        "--csv-path", csv_path,
        "--dest-path", "/tmp/viz/results/feature_"+str(quality_id)+".csv",
        "--image-path", src_path,
        "--mask-path", mask_path
    ]
       
    test = run(args, stdout=PIPE) #, capture_output=True)
    logger.info(f"Result: {test.stdout}")
    logger.error(f"Error: {test.stderr}",)

    ## upload csv
    #Popen(["python3.9", "./upload/upload_csv.py", "--path", "/tmp/viz/results/",
    #    "--csv_name", str(quality_id)],
    #       stdout=PIPE)

    csv_name = str(quality_id)+".csv"
    client_s3.upload_file(args.path+csv_name, bucket_name, "mask/"+csv_name)
    
    return { event }

if __name__ == "__main__":
    x = lambda_handler(
    {
        # "quality_id":90, 
        # "grape_id": {
        #     "start": 1501,
        #     "end" : 1652,
        #     "count": 152
        # }
        # 'quality_id': 91, 'grape_id': {"start": 5, "end": 56, "count": 52}
        'quality_id': 91, 'grape_id': '{"start": 301, "end": 378, "count": 78}'
    },1)
    print(x)