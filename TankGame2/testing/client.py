import socket
import threading
from collections import deque


class Client:
    def __init__(self):
        self.server_ip = '127.0.0.1'
        self.server_socket = None

        self.running = False
        self.offline_mode = False

        self.name = "Guest"
        self.name_list = []
        self.lobby_id = -1

        # a queue that holds data from the server
        self.buffer = []

    def connect(self, port=31410):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket.connect((self.server_ip, port))
        except ConnectionRefusedError:
            self.offline_mode = True

        if not self.offline_mode:
            self.running = True
            listening_thread = threading.Thread(target=self.listen, daemon=True)
            listening_thread.start()

    def disconnect(self):
        self.running = False
        self.server_socket.close()

    def listen(self):
        while self.running:

            data = self.server_socket.recv(1024)

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
        if self.server_socket is not None:
            self.server_socket.send(data.encode())
        else:
            print("no server found")

    # get the username of the owner of the current lobby
    def get_owner(self):
        for name in self.name_list:
            if name[-1] == '#':
                return name[:-1]

