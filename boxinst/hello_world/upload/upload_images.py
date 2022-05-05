import os
from boto3 import client
from argparse import ArgumentParser 

s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")

client_s3 = client( 's3',
        aws_access_key_id = s3_access_key,
        aws_secret_access_key = s3_secret_key
)


if __name__ == "__main__":
    parser = ArgumentParser(description='Send Images to S3.')
    parser.add_argument('--path', type=str)
    args = parser.parse_args()
    path = os.listdir(args.path)
    for file in path:
        client_s3.upload_file(
            args.path+file, bucket_name, 
            "public/result/"+file
        )
