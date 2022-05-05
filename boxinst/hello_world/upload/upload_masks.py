import os
from boto3 import client
from argparse import ArgumentParser 
from subprocess import run
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
    parser.add_argument('--quality_id', type=str)
    args = parser.parse_args()

    path = os.listdir(args.path)
    for file in path:
        client_s3.upload_file(
            args.path+file, bucket_name, 
            f"mask/{args.quality_id}/"+file
        )

#     zip_name = args.zip_name+".tar.gz"

#     test = run(["tar", "-zv", 
#         "-c", args.path,
#         "-f", zip_name, 
#         "--directory", args.path,
#         "--checkout"
#         ])
#     logger.info(f"Result: {test.stdout}")
#     logger.error(f"Error: {test.stderr}",)


#     client_s3.upload_file(args.path+zip_name, bucket_name, "mask/"+zip_name)
    logger.info(f"Uploaded Mask {args.quality_id} to S3")