import boto3
import hashlib


def upload_image_to_s3_bucket(path, bucket, image_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(path, bucket, image_name)


def create_hash(input_str):
    hash_object = hashlib.sha256(bytes(input_str, encoding='utf-8'))
    output = hash_object.hexdigest()
    return output
