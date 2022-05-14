import os
from boto3 import client
from argparse import ArgumentParser 
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
    parser = ArgumentParser(description='Send CSV to S3.')
    parser.add_argument('--path', type=str)
    parser.add_argument('--csv_name', type=str)
    args = parser.parse_args()

    csv_name = args.csv_name+".csv"

    client_s3.upload_file(args.path+csv_name, bucket_name, "mask/"+csv_name)
    logger.info(f"Uploaded CSV {csv_name} to S3")