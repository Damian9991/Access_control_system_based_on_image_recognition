#!/usr/bin/env python3

#-----------------------------------------------------------
# Name: Access_control_system_based_on_image_recognition
# Authors: Kamil Kryczka, Damian Osinka
# Thesis supervisor: dr hab. inz. Mikołaj Leszczuk
# Purpose: Engineering Thesis
# Created: 13-10-2018
#-----------------------------------------------------------


import os
import sys
import argparse
import boto3
import datetime
import cv2
from paramiko import SSHClient, AutoAddPolicy
from utils import *

import logging
logger = logging.getLogger("Access_control_system_based_on_image_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '').replace(' ', '') + "/Access_control_system_based_on_image_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


########################################################################################################################
#----------------------------------------------SetUpConnections class -------------------------------------------------#
########################################################################################################################

class RaspberryConnection(object):

    """ class is designed to start Access control system based on image recognition system
        -- set up connection with raspberry pi which is responsible for face detection and start streaming
        -- set up connection with raspberry pi which is responsible for licence plate recognition
    """

    def __init__(self, raspberry_face_ip, raspberry_plate_ip):
        logger.info("System Start")
        self.ssh_raspberry_face_connection = None
        self.ssh_raspberry_plate_connection = None
        self.raspberry_face_ip = raspberry_face_ip
        self.raspberry_plate_ip = raspberry_plate_ip
        self.create_ssh_connection(self.raspberry_face_ip, 22, "pi", "pi", "raspberry_face")
        self.create_ssh_connection(self.raspberry_plate_ip, 22, "pi", "pi", "raspberry_plate")

    def create_ssh_connection(self, address, port, user, password, raspberry_type, timeout=10):
        try:
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(address, port, user, password, timeout=timeout)
            if raspberry_type == "raspberry_face":
                self.ssh_raspberry_face_connection = ssh_client
                logger.info("ssh connection to raspberry_face has been created successfully")
            elif raspberry_type == "raspberry_plate":
                self.ssh_raspberry_plate_connection = ssh_client
                logger.info("ssh connection to raspberry plate has been created successfully")
        except Exception as err:
            logger.error("An error occured while creating SSH session: " + str(err))
            sys.exit(0)

    def start_stream(self):
        logger.info("Stream start")
        stream_command =  "nohup raspivid -o - -t 0 -hf -w 800 -h 400 -fps 24 |cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8160}' :demux=h264"
        stdin, stdout, stderr = self.ssh_raspberry_face_connection.exec_command(stream_command)
        logger.info(str(stdout))
        logger.error(str(stderr))

    def end_ssh_connection(self):
        logger.info("Stop ssh connections")
        try:
            self.ssh_raspberry_face_connection.close()
        except AttributeError as err:
            logger.warning(str(err))
        try:
            self.ssh_raspberry_plate_connection .close()
        except AttributeError as err:
            logger.warning(str(err))

########################################################################################################################
#----------------------------------------------FaceRecognition class -------------------------------------------------#
########################################################################################################################

class FaceRecognition(object):
    """ The class is responsible for face recognition with the use of AWS rekognition cloud system
        -- check whether the recognised face exists in collection; similarity should be above 80%
    """

    def __init__(self):
        self.faces_bucket = 'access-control-system-based-on-image-recognition-faces-eu-west'
        self.collection_id_faces = 'access-control-system-based-on-image-recognition-faces'
        self.client = boto3.client('rekognition')

    def search_for_face_in_collection(self, image_path):
        image_name = datetime.datetime.now().strftime("face_%d%m%Y_%H%M%S.jpg")
        upload_image_to_s3_bucket(image_path, self.faces_bucket, image_name)
        threshold = 80
        response_dict = self.client.search_faces_by_image(CollectionId=self.collection_id_faces,
                                                          Image={'S3Object': {'Bucket': self.faces_bucket,
                                                                              'Name': image_name}},
                                                          FaceMatchThreshold=threshold)

        face_matches = response_dict['FaceMatches']
        if face_matches:
            for match in face_matches:
                logger.info(match)
                logger.info('FaceId:' + match['Face']['FaceId'])
                logger.info('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                if match["Similarity"] > 80:
                    return match['Face']['ExternalImageId']
        else:
            return None

########################################################################################################################
#----------------------------------------------RaspberryObserver class ----------------------------------------------#
########################################################################################################################

class RaspberryAdministrator(object):

    """
        The class is designed to manage two raspberries and perform verification of any attempt to access the parking lot
        -- capture stream from raspberry responsible for face detection and try to find face
        -- take a picture on the raspberry responsible for licence plate recognition when the face is found
        -- manage an instance of FaceRecognition class
        -- manage an instance of RaspberryConnection class
        -- decide whether the driver has access to the parking lot
    """

    def __init__(self, raspberry_face_ip, raspberry_plate_ip):

        self.raspberry_face_ip = raspberry_face_ip
        self.raspberry_plate_ip = raspberry_plate_ip

        self.raspberries_connection = RaspberryConnection(self.raspberry_face_ip, self.raspberry_plate_ip)
        self.raspberries_connection.start_stream()
        self.face_recognition = FaceRecognition()

        self.licence_plate = None
        self.owner = None
        self.img_counter = 0

        self.photo_directory_path = os.popen("pwd").read().replace("\n", "") + "/face_photos/"
        if not os.path.exists(self.photo_directory_path):
            os.popen("mkdir " + self.photo_directory_path)

    def capture_stream_and_perform_access_verification(self):

        casc_path = "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(casc_path)
        video_source = "http://" + self.raspberry_face_ip + ":8160"

        try:
            video_capture = cv2.VideoCapture(video_source)
        except Exception as err:
            logger.error(str(err))
            sys.exit(0)
        while True:
            ret, frame = video_capture.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,
                    minNeighbors=5,
                    minSize=(70, 70),
                    flags=cv2.cv.CV_HAAR_SCALE_IMAGE
            )

            if len(faces) > 0:
                self.licence_plate = None
                self.owner = None

                self.recognise_licence_plate_number()
                self.save_face_photo(frame)
                self.owner = self.face_recognition.search_for_face_in_collection(<image_path_placeholder>)

                if self.owner is not None and self.check_if_driver_has_access(self.licence_plate, self.owner):
                    logger.info("OK")
                else:
                    logger.info("permission denied")

                video_capture = cv2.VideoCapture(video_source)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                video_capture.release()
                cv2.destroyAllWindows()
                break

            cv2.imshow('Video', frame)

    def recognise_licence_plate_number(self):
        python_script = "python /home/pi/licence_plate_recognition.py"
        stdin, stdout, stderr = self.raspberries_connection.ssh_raspberry_plate_connection.exec_command(python_script)
        logger.info(str(stdout))
        logger.error(str(stderr))
        self.licence_plate = stdout

    def save_face_photo(self, frame):
        img_name = "frame_{}.png".format(self.img_counter)
        resize = cv2.resize(frame, (500, 300))
        cv2.imwrite(self.photo_directory_path + img_name, resize)
        logger.info("{} written!".format(img_name))
        self.img_counter += 1

    @staticmethod
    def check_if_driver_has_access(licence_plate, owner):
        licence_plate_hash = create_hash(licence_plate)
        owner_hash = create_hash(owner)
        with open('database.json', mode='r', encoding='utf-8') as json_file:
            file_content = json.load(json_file)
        for user_dict in file_content:
            if licence_plate_hash in user_dict.keys():
                if owner_hash in user_dict[licence_plate_hash]:
                    logger.info(licence_plate)
                    logger.info(owner)
                    return True
                else:
                    logger.info('Licence plate number exists in database but does not belong to the driver')
            else:
                logger.info('Licence plate number does not exists in database')
        logger.info(licence_plate)
        logger.info(owner)
        return False

    def end_stream(self):
        pass


def get_arguments(parser):
    parser.add_argument("raspberry_face", "--raspberry_face", help = "raspberry_face ip address", required = True)
    parser.add_argument("raspberry_plate", "--raspberry_plate", help = "raspberry_plate ip address", required = True)
    args = vars(parser.parse_args())
    return args

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Access_control_system_based_on_image_recognition")
    args = get_arguments(parser)
    raspberry_face_ip = args['raspberry_face']
    raspberry_plate_ip = args['raspberry_plate']

    raspberry_administrator = RaspberryAdministrator(raspberry_face_ip, raspberry_plate_ip)
    raspberry_administrator.capture_stream_and_perform_access_verification()
