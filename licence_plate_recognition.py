import boto3
import datetime
import re
from utils import upload_image_to_s3_bucket


class LicencePlateRecognition:

    def __init__(self):
        self.licence_plates_bucket = 'access-control-system-based-on-image-recognition-licence-plates'
        self.collection_id_licence_plates = ''
        self.client = boto3.client('rekognition')

    def recognise_licence_plate(self, image_path):
        image_name = datetime.datetime.now().strftime("licence_plate_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(image_path, self.licence_plates_bucket, image_name)
        response = self.client.detect_text(Image={'S3Object': {'Bucket': self.licence_plates_bucket, 'Name': image_name}})

        detected_texts_dict = response['TextDetections']
        for text_dict in detected_texts_dict:
            if text_dict['Confidence'] > 80 and self.check_if_text_matches_to_licence_plate_regex(text_dict['DetectedText']):
                # print(text_dict['DetectedText'])
                return text_dict['DetectedText']

    @staticmethod
    def check_if_text_matches_to_licence_plate_regex(text):
        licence_plate_regex_list = [r'^[A-Z]{3}\ \w{4}$', r'^[A-Z]{2}\ \w{5}$', r'^[A-Z]\ \w{3}$']
        for regex in licence_plate_regex_list:
            if re.fullmatch(regex, text):
                return True
        return False

x = LicencePlateRecognition()
x.recognise_licence_plate('')
