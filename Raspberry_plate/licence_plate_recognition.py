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
import time
import picamera
import sys
sys.path.append('/home/pi/')
# from Access_control_system_based_on_image_recognition.Database.Database import DatabaseManager
from Access_control_system_based_on_image_recognition.utils import *

logger = logging.getLogger("licence_plate_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '') + "/licence_plate_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


class LicencePlateRecognition:

    def __init__(self):
        self.licence_plates_bucket = 'access-control-system-based-on-image-recognition-licence-plates'
        self.client = boto3.client('rekognition')
        self.image_dir_path = '/tmp/'
        self.image_path = None

    def recognise_licence_plate(self):
        start_time = time.time()
        image_name = datetime.datetime.now().strftime("licence_plate_%d%m%Y_%H%M%S.jpg")
        self.image_path = self.image_dir_path + image_name
        self.take_picture()
        upload_image_to_s3_bucket(self.image_path, self.licence_plates_bucket, image_name)
        start_time_response = time.time()
        response = self.client.detect_text(Image={'S3Object': {'Bucket': self.licence_plates_bucket, 'Name': image_name}})
        end_time_response = time.time()
        logger.info("Time elapsed while waiting for detect_text response: {}".format(end_time_response - start_time_response))
        delete_image_from_s3_bucket(self.licence_plates_bucket, image_name)
        
        detected_texts_dict = response['TextDetections']
        for text_dict in detected_texts_dict:
            if text_dict['Confidence'] > 80:
                    if self.check_if_text_matches_to_licence_plate_regex(text_dict['DetectedText']):
                        logger.info('Recognised licence number: {}'.format(text_dict['DetectedText']))
                        print(text_dict['DetectedText'])
                        end_time = time.time()
                        logger.info("Licence plate recognition time: {}".format(end_time - start_time))
                        return 0
                    logger.info('Text does not match licence plate regex')
            else:
                logger.info('Text is not clear enough for recognition: {}'.format(text_dict['DetectedText']))
        end_time = time.time()
        logger.info("Licence plate recognition time: {}".format(end_time - start_time))

    def take_picture(self):
        start_time = time.time()
        with picamera.PiCamera() as camera:
            camera.resolution = (320, 320)
            camera.capture(self.image_path)
        end_time = time.time()
        logger.info("take_picture method time: {}".format(end_time - start_time))

    @staticmethod
    def check_if_text_matches_to_licence_plate_regex(text):
        licence_plate_regex_list = [r'^[A-Z]{3}\ \w{4}$', r'^[A-Z]{2}\ \w{5}$', r'^[A-Z]\ \w{3}$']
        for regex in licence_plate_regex_list:
            if re.fullmatch(regex, text):
                return True
        return False

    # @staticmethod
    # def add_licence_plate_number_to_database(licence_plate, name):
    #     database_manager = DatabaseManager()
    #     database_manager.insert_into_licence_plates_table(name, licence_plate)
    #     database_manager.close_connection_to_db()


if __name__ == "__main__":
    plate_recognition = LicencePlateRecognition()
    plate_recognition.recognise_licence_plate()
