import socket
from paramiko import SSHClient, AutoAddPolicy



def create_ssh_connection(address, port, user, timeout=10):
    try:
        ssh_client = SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(hostname=address, port=port, username=user, timeout=timeout, allow_agent=False, look_for_keys=True)
        ssh_client.exec_command("python /home/pi/Desktop/TEST.py")
       # print(stderr.read())
        #print(stdout.read())



    except Exception as err:
        print(str(err))
        return None

create_ssh_connection('192.168.2.100', 22, "pi")