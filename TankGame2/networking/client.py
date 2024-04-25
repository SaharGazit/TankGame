import socket
import threading
from TankGame2.networking import protocol


class Client:
    def __init__(self):
        self.server_ip = '127.0.0.1'
        self.server_port_tcp = 31410
        self.server_socket_tcp = None
        self.server_socket_udp = None
        self.own_port = None

        self.running = False
        self.offline_mode = False

        self.name = "Guest"
        self.user_list = [[], []]
        self.lobby_id = -1

        # a queue that holds data from the server
        self.buffer = []

    def connect_tcp(self):
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket_tcp.connect((self.server_ip, self.server_port_tcp))
        except ConnectionRefusedError:
            self.offline_mode = True

        if not self.offline_mode:
            self.running = True
            listening_thread = threading.Thread(target=self.listen, daemon=True)
            listening_thread.start()

    def connect_udp(self):
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_port_udp = self.server_port_tcp + self.lobby_id
        self.server_socket_udp.sendto("R", (self.server_socket_udp, server_port_udp))

    def disconnect(self):
        self.running = False
        self.server_socket_tcp.close()

        if self.server_socket_udp is not None:
            self.server_socket_udp.close()

    def listen(self):
        while self.running:

            data = self.server_socket_tcp.recv(1024)
            print(data.decode())

            # push data to the buffer
            self.buffer.append(data.decode())

    def get_buffer_data(self, optional=True):
        # wait for data
        if not optional:
            while len(self.buffer) == 0:
                pass

        data = self.buffer.copy()
        self.buffer = []  # empty buffer
        return data

    def send_data(self, data):
        if self.server_socket_tcp is not None:
            self.server_socket_tcp.send(data.encode())
        else:
            print("no server found")

    # get the username of the owner of the current lobby
    def get_owner(self):
        for user in self.user_list[0] + self.user_list[1]:
            if user.owner:
                return user.name

    def update_lobby(self, data):
        data = data.split("|")
        self.lobby_id = data[0][1]

        # update user lists
        self.user_list = [[], []]
        for string in data[1:]:
            self.user_list[int(string[0]) - 1].append(protocol.User(string[1:], string[0]))

    def can_start(self):
        return self.get_owner() == self.name and len(self.user_list[0]) > 0 and len(self.user_list[1]) > 0
