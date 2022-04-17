import logging
import os
from boto3 import client
from argparse import ArgumentParser 
from subprocess import Popen , run
from logging import getLogger

s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")

client_s3 = client( 's3',
        aws_access_key_id = s3_access_key,
        aws_secret_access_key = s3_secret_key
)

logger = getLogger(__name__)
if __name__ == "__main__":
    parser = ArgumentParser(description='Send Masks to S3.')
    parser.add_argument('--path', type=str)
    parser.add_argument('--zip_name', type=str)
    args = parser.parse_args()
    #path = os.listdir(args.path)

    zip_name = args.zip_name+".tar.gz"

    test = run(["tar", "-zcvf", zip_name, args.path],
        capture_output=True)
    logger.info(f"Result: {test.stdout}")
    logger.error(f"Error: {test.stderr}",)


    client_s3.upload_file(zip_name, bucket_name, "mask/"+zip_name)
    logger.info(f"Uploaded Mask {zip_name} to S3")