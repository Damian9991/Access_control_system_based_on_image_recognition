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
import socket
from paramiko import SSHClient, AutoAddPolicy


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


def create_ssh_connection(address, port, user, timeout=10):
    try:
        address2 = "192.168.2.100"
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=address2, port=port, username=user, timeout=timeout, allow_agent=False, look_for_keys=True)
        return ssh_client
    except Exception as err:
        print(str(err))


def start_system(rasp_1_ip, rasp_2_ip):
    try:
        if check_system_status(rasp_1_ip) == "OFF":
            ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
            ssh_client.exec_command("python /home/pi/Desktop/TEST.py")
            return "ON"
        else:
            return "ALREADY_RUNNING"
    except Exception as err:
        print(str(err))

        
def check_system_status(rasp_1_ip):
    try:
        command = "pgrep -af TEST.py | awk '{print $1}' | xargs echo"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
        stdin, stdout, stderr = ssh_client.exec_command(command)
        print(stderr.read())
        if len(stdout.read().decode("utf-8").split(" ")) > 1:
            return "ON"
        else:
            return "OFF"

    except Exception as err:
        print(str(err))

        
def stop_system(rasp_1_ip):
    try:
        command = "pgrep -af TEST.py | awk '{print $1}' | xargs kill"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi')
        ssh_client.exec_command(command)
        return True
    except Exception as err:
        print(str(err))
