#!/usr/bin/env python3

# -----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
# -----------------------------------------------------------

import boto3
import hashlib


def upload_image_to_s3_bucket(path, bucket, image_name):
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(path, bucket, image_name)

def delete_image_from_s3_bucket(bucket, image_name):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, image_name)
    obj.delete()

def create_hash(input_str):
    hash_object = hashlib.sha256(bytes(input_str, encoding='utf-8'))
    output = hash_object.hexdigest()
    return output
