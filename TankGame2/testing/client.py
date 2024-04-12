import socket
import threading
from collections import deque


class Client:
    def __init__(self):
        self.server_ip = '127.0.0.1'
        self.server_socket = None

        self.running = False

        # a queue that holds data from the server
        self.buffer = []

    def connect(self, port=31410):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((self.server_ip, port))

        self.running = True
        listening_thread = threading.Thread(target=self.listen, daemon=True)
        listening_thread.start()

    def disconnect(self):
        self.running = False
        self.server_socket.close()

    def listen(self):
        while self.running:

            # get data
            data = self.server_socket.recv(1024)

            # push data to the buffer
            self.buffer.append(data.decode())

    def get_buffer_data(self):
        data = self.buffer.copy()
        self.buffer = []  # empty buffer
        return data

    def send_data(self, data):
        if self.server_socket is not None:
            self.server_socket.send(data.encode())
        else:
            print("no server found")

