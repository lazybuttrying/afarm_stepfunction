from os import environ
from boto3 import client
from argparse import ArgumentParser 
from logging import getLogger


s3_access_key = environ.get("S3_ACCESS_KEY")
s3_secret_key = environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = environ.get("BUCKET_NAME")

client_s3 = client( 's3',
        aws_access_key_id = s3_access_key,
        aws_secret_access_key = s3_secret_key
)


if __name__ == "__main__":
    parser = ArgumentParser(description='Send an Image to S3.')
    parser.add_argument('--path', type=str)
    parser.add_argument('--file_name', type=str)
     
    args = parser.parse_args()
    path, fname = args.path, args.file_name
    client_s3.upload_file(
        path, bucket_name, 
        "public/result/"+fname
    )
    logger = getLogger(__name__)
    logger.info("Send an Image to S3 : ", fname)
