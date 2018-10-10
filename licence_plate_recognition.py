import boto3
import datetime


class FaceRecognition:

    def __init__(self):
        self.licence_plates_bucket = 'access-control-system-based-on-image-recognition-licence-plates'
        self.collection_id_licence_plates = ''
        self.client = boto3.client('rekognition')


