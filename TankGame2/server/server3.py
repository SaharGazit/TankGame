import protocol
import socket
import threading


class VoiceChatServer:

    # initiates the voice chat server
    # lobby_id - the correct voice server port for this lobby is equal to protocol.vcserver_port plus the lobby id
    # so for example, if protocol.vcserver_port is 40000, and this lobby is number 10, the port would be 40010
    def __init__(self, lobby_id):
        # server IP and port
        self.host = '0.0.0.0'
        self.port = protocol.vcserver_port + lobby_id

        # create a UDP socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        # timeout: the server stops listening if it doesn't get anything for a second
        self.server_socket.settimeout(1)

        self.clients = {}  # dictionary of socket addresses and names
        self.running = False  # true as long as the server is running

    # starts listening for audio from the clients
    # users - dictionary that consists of socket addresses and their username
    def start(self, users):
        self.clients = users
        self.running = True
        # starts listening thread
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

    # tells the listening thread to stop, and resets the client list
    def stop(self):
        self.clients = {}
        self.running = False

    # receives audio data, adds the sender's username to the data, and broadcasts it to the rest of the clients.
    def listen(self):
        while self.running:
            try:
                data, client_address = self.server_socket.recvfrom(4096)
                if client_address in self.clients.keys():
                    # add client index to the message
                    data = f"{self.clients[client_address]}||".encode() + data

                    self.broadcast(data, client_address)
            # timeout is triggered after no client sends anything, to check if self.running is still true.
            # this is to prevent the program to get stuck waiting for data, while it actually supposed to stop.
            except socket.timeout:
                continue
            # prevents the server from crashing if a client has disconnected.
            except ConnectionResetError:
                continue

    # sends data to every client
    # data - the data (in bytes) that should be sent
    # sender_address - the address that shouldn't get this data (typically the address that triggered this broadcasting)
    def broadcast(self, data, sender_address):
        for client_address in self.clients.keys():
            if client_address != sender_address:
                self.server_socket.sendto(data, client_address)
