#!/usr/bin/env python3

import boto3
import hashlib
import socket
import logging
import os
import time
from paramiko import SSHClient, AutoAddPolicy

logger = logging.getLogger("utils")
hdlr = logging.FileHandler(os.popen("pwd").read().replace('\n', '') + "/utils.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def upload_image_to_s3_bucket(path, bucket, image_name):
    start_time = time.time()
    s3 = boto3.resource('s3')
    s3.meta.client.upload_file(path, bucket, image_name)
    end_time = time.time()
    logger.info("Image {} uploading time: {}".format(path, end_time-start_time))

    
def delete_image_from_s3_bucket(bucket, image_name):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket, image_name)
    obj.delete()
    logger.info("image: {} has been deleted".format(image_name))

    
def create_hash(input_str):
    logger.info("Creating hash: " + input_str)
    hash_object = hashlib.sha256(bytes(input_str, encoding='utf-8'))
    output = hash_object.hexdigest()
    return output


def create_ssh_connection(address, port, user, timeout=10):
    try:
        address = "192.168.0.19"
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=address, port=port, username=user, timeout=timeout, allow_agent=False, look_for_keys=True)
        return ssh_client
    except Exception as err:
        logger.error(str(err))


def start_system(rasp_1_ip, rasp_2_ip):
    try:
        logger.info("Starting system...")
        if True:
        #if check_system_status(rasp_1_ip) == "OFF":
            ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
            ssh_client.exec_command("python /home/pi/Desktop/Access_control_system_based_on_image_recognition/Raspberry_face/run_system.py --raspberry_plate " + "192.168.43.132")
            logger.info("System started successfully")
            return "ON"
        else:
            logger.info("System already running!")
            return "ALREADY_RUNNING"
    except Exception as err:
        print(str(err))
        logger.error(str(err))

        
def check_system_status(rasp_1_ip):
    try:
        command = "pgrep -af run_system.py | awk '{print $1}' | xargs echo"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
        stdin, stdout, stderr = ssh_client.exec_command(command)
        logger.info("Checking system status ...")
        logger.info(stdout.read())
        logger.info(stderr.read())
        if len(stdout.read().decode("utf-8").split(" ")) > 1:
            logger.info("Status is ON")
            return "ON"
        else:
            logger.info("Status is OFF")
            return "OFF"
    except Exception as err:
        logger.error(str(err))

        
def stop_system(rasp_1_ip):
    try:
        logger.info("Stopping system...")
        command = "pgrep -af TEST.py | awk '{print $1}' | xargs kill"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
        ssh_client.exec_command(command)
        logger.info("System stopped successfully")
        return True
    except Exception as err:
        logger.error(str(err))
