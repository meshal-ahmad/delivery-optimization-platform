import boto3
import os
from dotenv import dotenv_values

config = dotenv_values(".env")

AWS_ACCESS_KEY_ID     = config["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = config["AWS_SECRET_ACCESS_KEY"]
AWS_REGION            = config["AWS_REGION"]
S3_BUCKET             = config["S3_BUCKET"]

s3 = boto3.client(
    "s3",
    aws_access_key_id     = AWS_ACCESS_KEY_ID,
    aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
    region_name           = AWS_REGION
)

files = [
    ("data/raw/orders.csv",       "raw/orders/orders.csv"),
    ("data/raw/captains.csv",     "raw/captains/captains.csv"),
    ("data/raw/restaurants.csv",  "raw/restaurants/restaurants.csv"),
]

print("=" * 55)
print("  Uploading files to S3...")
print("=" * 55)

for local_path, s3_key in files:
    print(f"  Uploading {local_path} ...")
    s3.upload_file(local_path, S3_BUCKET, s3_key)
    print(f"  Done: s3://{S3_BUCKET}/{s3_key}")

print("\n" + "=" * 55)
print("  ALL FILES UPLOADED SUCCESSFULLY")
print("=" * 55)