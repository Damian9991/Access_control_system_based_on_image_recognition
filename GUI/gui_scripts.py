import socket
from paramiko import SSHClient, AutoAddPolicy


def create_ssh_connection(address, port, user, password, timeout=10):
    try:
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(address, port, user, password, timeout=timeout)
        return ssh_client
    except Exception as err:
        return None

def start_system(rasp_1_ip, rasp_2_ip):
    try:
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi', 'pi')
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command("START.py " + rasp_2_ip)
        else:
            return False
    except socket.error:
        return False

def check_system_status(rasp_1_ip):
    try:
        command = "pgrep -af gui | awk '{print $1}' | xargs echo"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi', 'pi')
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(command)
        else:
            return False
    except socket.error:
        return False


def stop_system(rasp_1_ip):
    try:
        command = "pgrep -af gui | awk '{print $1}' | xargs kill"
        ssh_client = create_ssh_connection(rasp_1_ip, 22, 'pi', 'pi')
        if ssh_client:
            stdin, stdout, stderr = ssh_client.exec_command(command)
        else:
            return False
    except socket.error:
        return False

