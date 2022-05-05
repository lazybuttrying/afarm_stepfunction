import os
from boto3 import resource
from argparse import ArgumentParser 
from logging import getLogger

s3_access_key = os.environ.get("S3_ACCESS_KEY")
s3_secret_key = os.environ.get("S3_SECRET_ACCESS_KEY")
bucket_name = os.environ.get("BUCKET_NAME")

resource_s3 = resource( 's3', 
    aws_access_key_id=s3_access_key,
    aws_secret_access_key=s3_secret_key
)

bucket = resource_s3.Bucket(bucket_name)

logger = getLogger(__name__)
if __name__ == "__main__":
    parser = ArgumentParser(description='Download Masks from S3.')
    parser.add_argument('--mask_path', type=str)
    parser.add_argument('--quality_id', type=str)
    args = parser.parse_args()
    quality_id = args.quality_id
    mask_path = args.mask_path

    src_s3 = "mask/"+str(quality_id)+"/"
    for obj in bucket.objects.filter(Prefix=src_s3):
        if obj.key[-1] != "/":
            fname = obj.key.split("/")[-1]
            bucket.download_file(obj.key, mask_path+fname)

    logger.info(f"Download Masks from S3")