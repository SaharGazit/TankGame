import socket

from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

server_ip = "127.0.0.1"
server_port = 30000
vcserver_port = 40000
MAX_PLAYERS_IN_LOBBY = 8

BYTE_CHUNK = 2024
VC_BYTE_CHUNK = 4096


class User:
    def __init__(self, name="guest", team=0, addr=None):  # no socket, since it's already a part of a dictionary
        self.logged = name != "guest"
        self.authenticated = False

        if name[-1] == "#":
            name = name[:-1]
            self.owner = True
        else:
            self.owner = False

        self.address = addr
        self.name = name
        self.team = team

        self.volume_factor = 0

    def login(self, username):
        self.name = username
        self.logged = True

    def logout(self):
        self.name = "guest"
        self.logged = False

    min_radius = 400
    max_radius = 1000

    def set_volume_factor(self, distance_to_main):
        if distance_to_main < User.min_radius:
            self.volume_factor = 1
        elif distance_to_main <= User.max_radius:
            self.volume_factor = (User.max_radius - distance_to_main) / (User.max_radius - User.min_radius)
        else:
            self.volume_factor = 0


def send_data(data, sock, addr=None):
    sock_type = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
    if sock_type == socket.SOCK_STREAM:
        sock.sendall(data)
    elif sock_type == socket.SOCK_DGRAM:
        sock.sendto(data, addr)


def receive_data(sock, vc=False):
    sock_type = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
    data = ""
    if sock_type == socket.SOCK_STREAM:
        data = sock.recv(BYTE_CHUNK)
    elif sock_type == socket.SOCK_DGRAM:
        if vc:
            data = sock.recvfrom(VC_BYTE_CHUNK)
        else:
            data = sock.recvfrom(BYTE_CHUNK)

    return data


def encrypt_data(key, data):
    # Generate a random IV (Initialization Vector)
    iv = get_random_bytes(16)

    # Create AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Pad the data to be multiple of block size
    padded_data = pad(data, AES.block_size)

    # Encrypt the data
    encrypted_data = cipher.encrypt(padded_data)

    # Return the IV and encrypted data
    return iv + encrypted_data


def decrypt_data(key, encrypted_data):
    # Extract the IV from the beginning of the encrypted data
    iv = encrypted_data[:16]

    # Extract the actual encrypted data
    actual_encrypted_data = encrypted_data[16:]

    # Create AES cipher
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Decrypt the data
    decrypted_data = cipher.decrypt(actual_encrypted_data)

    # Unpad the data
    original_data = unpad(decrypted_data, AES.block_size)

    # Return the original data
    return original_data
