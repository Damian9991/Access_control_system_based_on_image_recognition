#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys
sys.path.append("../")
import datetime
import cv2
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import RPi.GPIO as GPIO
from multiprocessing.pool import ThreadPool
from paramiko import SSHClient, AutoAddPolicy
from utils import *
from Raspberry_face.face_recognition import FaceRecognition
from Database.Database import DatabaseManager

logger = logging.getLogger("Access_control_system_based_on_image_recognition")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '') + "/Access_control_system_based_on_image_recognition.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


########################################################################################################################
# -------------------------------------------- RaspberryConnection class --------------------------------------------- #
########################################################################################################################

class RaspberryConnection(object):

    """ The class is designed to initiate the connection to Raspberry responsible for licence plate recognition
    """

    def __init__(self, second_raspberry_ip):
        self.ssh_raspberry_plate_connection = None
        self.second_raspberry = second_raspberry_ip
        self.create_ssh_connection_to_second_raspberry(self.second_raspberry, 22, "pi")

    def create_ssh_connection_to_second_raspberry(self, address, port, user, timeout=10):
        try:
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(hostname=address, port=port, username=user, timeout=timeout, allow_agent=False, look_for_keys=True)
            self.ssh_raspberry_plate_connection = ssh_client
            logger.info("ssh connection to licence plate Raspberry has been created successfully")
        except Exception as err:
            logger.error("An error occurred while creating SSH session: " + str(err))
            sys.exit(0)

    def end_ssh_connection(self):
        logger.info("Stop ssh connection")
        try:
            self.ssh_raspberry_plate_connection.close()
        except AttributeError as err:
            logger.warning(str(err))


########################################################################################################################
# -------------------------------------------- DiodesManagement class ------------------------------------------------ #
########################################################################################################################

class DiodesManagement(object):

        def __init__(self):
            self.green_diode_pin = 21
            self.red_diode_pin = 20
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)

        def turn_on_diode(self, color, on_time=1.0):
            try:
                if color == "green":
                    pin = self.green_diode_pin
                else:
                    pin = self.red_diode_pin

                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)
                time.sleep(on_time)

            except Exception as err:
                logger.error(str(err))

            finally:
                GPIO.cleanup()


########################################################################################################################
# --------------------------------------------- RaspberryAdministrator class ----------------------------------------- #
########################################################################################################################

class RaspberryAdministrator(object):

    """
        The class is designed to manage two Raspberries and perform verification of any attempt to access the parking lot
        -- capture stream from Raspberry responsible for face detection and try to find face
        -- take a picture on the Raspberry responsible for licence plate recognition when the face is found
        -- manage an instance of FaceRecognition class
        -- manage an instance of RaspberryConnection class
        -- decide whether the driver has access to the parking lot
        """

    def __init__(self, raspberry_plate_ip):
        logger.info("System Start")

        self.raspberry_plate_ip = raspberry_plate_ip
        self.raspberry_connection = RaspberryConnection(self.raspberry_plate_ip)
        self.face_recognition = FaceRecognition()
        self.database = DatabaseManager()

        self.licence_plate = None
        self.owner = None
        self.diodes = None

        self.photo_directory_path = "/tmp/"

    def capture_stream_and_perform_access_verification(self):
        casc_path = "haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(casc_path)

        try:
            camera = PiCamera()
            camera.resolution = (320, 240)
            camera.framerate = 8
            rawCapture = PiRGBArray(camera, size=(320, 240))
            time.sleep(0.1)
        except Exception as err:
            logger.error(str(err))
            sys.exit(0)
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            image = frame.array
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 5)

            if len(faces) > 0:
                start_time = time.time()
                self.licence_plate = None
                self.owner = None
                pool = ThreadPool(processes=1)
                async_result = pool.apply_async(self.recognise_licence_plate_number, ())

                try:
                    self.recognise_face(image)
                except Exception as err:
                    logger.error(str(err))
                    self.diodes.turn_on_diode(color="red")

                self.licence_plate = async_result.get()
                end_time = time.time()
                self.diodes = DiodesManagement()
                if self.owner is not None and self.check_if_driver_has_access(self.licence_plate, self.owner):
                    self.diodes.turn_on_diode(color="green")
                    logger.info("Access granted")
                else:
                    self.diodes.turn_on_diode(color="red")
                    logger.warning("Access denied!")

                logger.info("Verification time: {}".format(end_time-start_time))
                logger.info("sleeping 5 seconds")
                time.sleep(5)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                self.raspberry_connection.end_ssh_connection()
                break
            rawCapture.truncate(0)

    def recognise_licence_plate_number(self):
        logger.info("recognise_licence_plate_number start")
        start_time = time.time()
        python_script = "python3 /home/pi/Access_control_system_based_on_image_recognition/Raspberry_plate/licence_plate_recognition.py"
        stdin, stdout, stderr = self.raspberry_connection.ssh_raspberry_plate_connection.exec_command(python_script)
        stdin.close()
        logger.info("output from plate recognition script: {}".format(self.licence_plate))
        end_time = time.time()
        logger.info("recognise_licence_plate_number method finished. Time elapsed: {}".format(end_time - start_time))
        return stdout.read().decode().strip()

    def recognise_face(self, frame):
        logger.info("recognise_face start")
        start_time = time.time()
        image_path = self.save_face_photo(frame)
        self.owner = self.face_recognition.search_for_face_in_collection(image_path)
        logger.info("self.owner = {}".format(self.owner))
        end_time = time.time()
        logger.info("recognise_face method finished. Time elapsed: {}".format(end_time-start_time))

    def save_face_photo(self, frame):
        image_name = datetime.datetime.now().strftime("frame_%d%m%Y_%H%M%S.jpg")
        image_path = self.photo_directory_path + image_name
        resize = cv2.resize(frame, (320, 240))
        cv2.imwrite(image_path, resize)
        logger.info("{} written!".format(image_path))
        return image_path

    def check_if_driver_has_access(self, licence_plate, owner):
        licence_plates_from_db = self.database.get_licence_plates_from_db(owner)
        logger.info("licence_plates_from_db = {}".format(licence_plates_from_db))
        logger.info("licence_plate = {}".format(licence_plate))
        if licence_plates_from_db:
            if licence_plate in licence_plates_from_db:
                    logger.info("check_if_driver_has_access method returns True")
                    return True
        else:
            if self.database.check_if_user_in_database(owner):
                logger.info("User exists in database but is assigned to different licence plate number!")
            else:
                logger.info("User does not exist in database!")
        logger.info("check_if_driver_has_access method returns False")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Access_control_system_based_on_image_recognition")
    parser.add_argument("--secondary_raspberry", help="Licence plate Raspberry IP address", required=True)
    args = vars(parser.parse_args())
    raspberry_plate_ip = args['secondary_raspberry']

    raspberry_administrator = RaspberryAdministrator(raspberry_plate_ip)
    raspberry_administrator.capture_stream_and_perform_access_verification()
