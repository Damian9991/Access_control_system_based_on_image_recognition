#!/usr/bin/env python3

# -----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
# -----------------------------------------------------------

import boto3
import datetime
import re
import logging
import os
import picamera
from Database.Database import DatabaseManager
from utils import upload_image_to_s3_bucket, create_hash

logger = logging.getLogger("Access_control_system_based_on_image_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read() + "/licence_plate_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class LicencePlateRecognition:

    def __init__(self):
        self.licence_plates_bucket = 'access-control-system-based-on-image-recognition-licence-plates'
        self.collection_id_licence_plates = ''
        self.client = boto3.client('rekognition')
        self.image_path = '/tmp/licence_plate.jpg'

    def recognise_licence_plate(self):
        self.take_picture()
        image_name = datetime.datetime.now().strftime("licence_plate_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(self.image_path, self.licence_plates_bucket, image_name)
        response = self.client.detect_text(Image={'S3Object': {'Bucket': self.licence_plates_bucket, 'Name': image_name}})

        detected_texts_dict = response['TextDetections']
        for text_dict in detected_texts_dict:
            if text_dict['Confidence'] > 80:
                    if self.check_if_text_matches_to_licence_plate_regex(text_dict['DetectedText']):
                        logger.info('Verification successful, access granted for licence number: '.format(text_dict['DetectedText']))
                        return text_dict['DetectedText']
                    logger.info('Licence plate number not found id database, access denied for licence number: '.format(text_dict['DetectedText']))
            else:
                logger.info('Picture did not contain any clear text')
        return None

    def take_picture(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 640)
            camera.capture(self.image_path)

    @staticmethod
    def check_if_text_matches_to_licence_plate_regex(text):
        licence_plate_regex_list = [r'^[A-Z]{3}\ \w{4}$', r'^[A-Z]{2}\ \w{5}$', r'^[A-Z]\ \w{3}$']
        for regex in licence_plate_regex_list:
            if re.fullmatch(regex, text):
                return True
        return False

    @staticmethod
    def add_licence_plate_number_to_database(licence_plate, name):
        licence_plate_hash = create_hash(licence_plate)
        name_hash = create_hash(name)
        database_manager = DatabaseManager()
        database_manager.insert_data('licence_plates', name_hash, licence_plate_hash)
        database_manager.close_connection_to_db()


if __name__ == "__main__":
    plate_recognition = LicencePlateRecognition()
    plate_recognition.recognise_licence_plate()
