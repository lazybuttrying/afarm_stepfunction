from datetime import datetime as dt
from csv import reader
from dotenv import load_dotenv
from requests import request
from subprocess import Popen, run, PIPE
import os
from boto3 import resource
import logging
from json import dumps

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

headers = {
    "Content-Type":"application/json",
    "x-hasura-admin-secret": hasura_key
}

resource_s3 = resource( 's3', 
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

bucket = resource_s3.Bucket(bucket_name)


def lambda_handler(event, context):
    logger = logging.getLogger(__name__)
    # mkdir image folders
    quality_id = event[0]["quality_id"]
    grape_id = event[0]["grape_id"]
    src_path = root_path+'img/'+str(quality_id)+"/"
    dest_path = root_path+'viz/'+str(quality_id)+"/"
    mask_path = root_path+'regression_data/masks/'+str(quality_id)+"/"
    
    os.makedirs(root_path+'viz/results/', exist_ok = True)
    os.makedirs(src_path, exist_ok = True)
    os.makedirs(dest_path, exist_ok = True)
    os.makedirs(mask_path, exist_ok = True)

    # # download images
    src_s3 = "grape_before/"+str(quality_id)+"/"
    for obj in bucket.objects.filter(Prefix=src_s3):
        if obj.key[-1] != "/":
            fname = str(dt.now()).replace(" ", "_")+obj.key.split("/")[-1]
            bucket.download_file(obj.key, src_path+fname)
    
            
    args = ['python3.9', "/var/task/box/demo/demo.py", 
        "--code", str(quality_id), 
        "--input", src_path,
        "--output", dest_path,
        "--mask-path", mask_path,
        "--opts", "MODEL.DEVICE", "cpu",
            "MODEL.WEIGHTS", "/var/task/box/training_dir/BoxInst_MS_R_50_1x_sick4/model_0059999.pth"]
       
    test = run(args, stdout=PIPE) #, capture_output=True)
    logger.info(f"Result: {test.stdout}")
    logger.error(f"Error: {test.stderr}",)


    # get result
    result_csv = reader(open(root_path+'viz/results/'+str(quality_id)+'.csv'))
    
   
    Popen(["python3.9", "upload_csv.py", "--path", root_path+'viz/results/',
        "--csv_name", str(quality_id)],
        stdout=PIPE)
    Popen(["python3.9", "upload_masks.py", "--path", mask_path,
        "--quality_id", str(quality_id)],
        stdout=PIPE)
    # upload result to s3 and prepare GraphQL payload
    payload_grapes = ""
    start_grape_id = grape_id+1
    for row in result_csv:
        grape_id += 1
        # tensor([0, 0, 0])
        pred_classes = row[-2][8:-2].split(", ")
        sick_berry = pred_classes.count("1")
        berry = len(pred_classes) - sick_berry
        payload_grapes += objs % (quality_id, grape_id, berry, sick_berry, row[-1].split('/')[-1] )

     # save all the data
    response = request("POST", url, headers=headers, 
                 data = payload_objs % (payload_grapes)).json()
    logger.info(f"Response of hasura : {response}") 


    return {
        "statusCode": 200,
        "quality_id": quality_id,
        "grape_id": dumps({
            "start" : start_grape_id,
            "end" : grape_id,
            "count" : grape_id-start_grape_id+1
        })
    }


if __name__ == "__main__":
    x = lambda_handler([{"quality_id":90, "grape_id":1500}],1)
    print(x)