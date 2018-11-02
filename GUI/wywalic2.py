
from paramiko import SSHClient, AutoAddPolicy



class RaspberryConnection(object):

    """ The class is designed to initiate the connection to Raspberry responsible for licence plate recognition
    """

    def __init__(self, second_raspberry_ip):
        self.ssh_raspberry_plate_connection = None
        self.second_raspberry = second_raspberry_ip
        self.create_ssh_connection_to_second_raspberry(self.second_raspberry, 22, "pi", "pi")

    def create_ssh_connection_to_second_raspberry(self, address, port, user, password, timeout=10):
        try:
            ssh_client = SSHClient()
            ssh_client.load_system_host_keys()
            ssh_client.set_missing_host_key_policy(AutoAddPolicy())
            ssh_client.connect(hostname=address, port=port, username=user, timeout=timeout, allow_agent=False, look_for_keys=True)
            #ssh_client.connect(address, port, user, password, timeout=timeout)
            self.ssh_raspberry_plate_connection = ssh_client

            stdin, stdout, stderr = ssh_client.exec_command("ls")
            print(str(stdout.read()))
            print(str(stderr))

        except Exception as err:
            print(str(err))

ob = RaspberryConnection("192.168.43.156")
ob.create_ssh_connection_to_second_raspberry("192.168.43.156", "22", "pi", "parkour2020")