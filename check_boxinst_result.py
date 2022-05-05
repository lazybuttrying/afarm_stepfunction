import requests
import boto3
import json

# pip3 install -t requests .
def lambda_handler(event, context):
    quality_id = event["quality_id"]
    log = {}

    bucket_name = 'afarm7defa4de003f406bbc7d6b4bdadbe11820155-dev'
    client_s3 = boto3.client( 's3',
        aws_access_key_id = 'AKIATT5FWZ7HYVXPO7GF',
        aws_secret_access_key = '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',
    )

    prefix = 'grape_before/'+str(quality_id)+"/"
    objs = client_s3.list_objects(Bucket=bucket_name, Prefix=prefix)
        
    if "Contents" not in objs or len(objs["Contents"]) <= 2:
        return { "statusCode":200, "log": json.dumps({"msg":"empty"}) }
    objs = objs["Contents"]
    
    
    
    url = "https://better-rat-41.hasura.app/v1/graphql"
    payload="{\"query\":\"mutation MyMutation {\\r\\n  delete_afarm_grape(where: {quality_id: {_eq: %s}}) {\\r\\n    returning {\\r\\n      grape_id\\r\\n    }\\r\\n  }\\r\\n}\\r\\n\",\"variables\":{}}"
    headers = {
      'x-hasura-admin-secret': 'i7IqYmNWceH9bKQAtqMy5hIdujfvMQCeKjJf2JadYfFbhvXug2xatLayZB0HDFLA',
      'Content-Type': 'application/json'
    }
    
    
    try:
        hasura_response = requests.request("POST", url, headers=headers, 
            data=payload % str(quality_id)).text
        log["hasura"] = hasura_response
    except:
        log["hasura"] = "No data in hasura or just failed to delete"


    try:
        s3_response = client_s3.delete_objects(Bucket=bucket_name, 
            Delete = { 'Objects':[
                {'Key':objs[x]['Key']} for x in range(len(objs))]})
        log["s3"] = s3_response
    except:
        log["s3"] = "failed to delete files in s3"
     
     
        
    return { "statusCode": 200, "quality_id":quality_id, "log":json.dumps(log)}

            