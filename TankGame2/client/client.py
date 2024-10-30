import socket
import threading

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from . import VoiceChatClient, protocol


class Client:
    def __init__(self):
        self.server_ip = protocol.server_ip
        self.server_port_tcp = protocol.server_port
        self.server_port_udp = None
        self.server_socket_tcp = None
        self.server_socket_udp = None
        self.own_port = None

        self.running_tcp = False
        self.running_udp = False
        self.offline_mode = False

        self.name = "Guest"
        self.user_list = [[], []]
        self.lobby_id = -1

        self.vcclient = None
        self.logged = False

        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.public_key()
        self.aes_key = None

        # A queue that holds the data from the server
        self.buffer = []

    def connect_tcp(self):
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket_tcp.connect((self.server_ip, self.server_port_tcp))
            self.own_port = self.server_socket_tcp.getsockname()[1]
            protocol.send_data(self.public_key.export_key(), self.server_socket_tcp)
        except ConnectionRefusedError:
            self.offline_mode = True

        if not self.offline_mode:
            self.running_tcp = True
            listening_thread = threading.Thread(target=self.listen_tcp, daemon=True)
            listening_thread.start()

    def connect_udp(self):
        self.running_udp = True
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket_udp.bind(("0.0.0.0", self.own_port + 1))

        self.server_port_udp = self.server_port_tcp + self.lobby_id
        data = protocol.encrypt_data(self.aes_key, b"R")
        protocol.send_data(data, self.server_socket_udp, (self.server_ip, self.server_port_udp))

        listening_thread = threading.Thread(target=self.listen_udp, daemon=True)
        listening_thread.start()

    def disconnect_udp(self):
        self.running_udp = False
        if self.server_socket_udp is not None:
            self.server_socket_udp.close()

    def listen_tcp(self):
        while self.running_tcp:

            data = protocol.receive_data(self.server_socket_tcp)

            if self.aes_key is None:
                # Get the encryption key
                self.aes_key = self.decrypt_aes_key(data)
                print("Received and decrypted AES key:", self.aes_key)
            elif len(data) > 0:
                data = protocol.decrypt_data(self.aes_key, data)
                # Push data to the buffer
                self.buffer.append(data.decode())

    def listen_udp(self):
        try:
            while self.running_udp:
                data, addr = protocol.receive_data(self.server_socket_udp)
                data = protocol.decrypt_data(self.aes_key, data).decode()

                if addr == (self.server_ip, self.server_port_udp):
                    # push data to the buffer
                    self.buffer.append(data)
        except OSError:
            self.running_udp = False

    def get_buffer_data(self, optional=True):
        # wait for data
        if not optional:
            while len(self.buffer) == 0:
                pass

        data = self.buffer.copy()
        self.buffer = []  # empty buffer
        return data

    def send_data(self, data):
        data = protocol.encrypt_data(self.aes_key, data.encode())
        protocol.send_data(data, self.server_socket_tcp)

    def send_player_status(self, data):
        data = protocol.encrypt_data(self.aes_key, f"{self.name}|{data}".encode())
        protocol.send_data(data, self.server_socket_udp, (self.server_ip, self.server_port_udp))

    # get the username of the owner of the current lobby
    def get_owner(self, raw=False):
        for user in self.user_list[0] + self.user_list[1]:
            if user.owner:
                if raw:
                    return user
                return user.name
        return None

    def get_dummy_user(self):
        return protocol.User(self.name, 0)

    def update_lobby(self, data):
        data = data.split("|")
        self.lobby_id = int(data[0][1])

        # Get list
        if data[1] == "list":
            # Update user lists
            self.user_list = [[], []]
            for string in data[2:]:
                self.user_list[int(string[0]) - 1].append(protocol.User(string[1:], int(string[0])))
        # Add a player
        elif data[1] == "join":
            # add new user
            team = int(data[3])
            self.user_list[team - 1].append(protocol.User(data[2], team))
        elif data[1] == "leave":
            # remove user
            for t in range(2):
                for user in self.user_list[t]:
                    if user.name == data[2]:
                        self.user_list[t].remove(user)
                        break
        elif data[1] == "promote":
            for user in self.user_list[0] + self.user_list[1]:
                # Promote a new owner (also demote the old one)
                user.owner = user.name == data[2]


    def can_start(self):
        return self.get_owner() == self.name and len(self.user_list[0]) > 0 and len(self.user_list[1]) > 0

    def start_voice_client(self):
        self.vcclient = VoiceChatClient(self.lobby_id, self.own_port, self.aes_key)
        self.vcclient.start(self.user_list[0] + self.user_list[1])

    def stop_voice_client(self):
        self.vcclient.running = False
        self.vcclient.client_socket.close()

    def login(self, name):
        self.name = name
        self.logged = True

    def decrypt_aes_key(self, encrypted_aes_key):
        cipher_rsa = PKCS1_OAEP.new(self.private_key)
        aes_key = cipher_rsa.decrypt(encrypted_aes_key)
        return aes_key
