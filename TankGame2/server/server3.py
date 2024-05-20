import protocol
import socket
import threading


class VoiceChatServer:
    def __init__(self, id_):
        self.host = '0.0.0.0'  # Server IP
        self.port = protocol.vcserver_port + id_  # Server port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.settimeout(0.1)

        self.clients = {}
        self.running = False

    def start(self):
        self.running = True
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

    def stop(self):
        self.clients = {}
        self.running = False

    def listen(self):
        while self.running:
            try:
                data, client_address = self.server_socket.recvfrom(4096)
                if client_address in self.clients.keys():
                    # add client index to the message
                    data = f"{self.clients[client_address]}||".encode() + data

                    self.broadcast(data, client_address)
            except socket.timeout:
                continue
            except ConnectionResetError:
                continue

    def broadcast(self, data, sender_address):
        for client_address in self.clients.keys():
            if client_address != sender_address:
                self.server_socket.sendto(data, client_address)
