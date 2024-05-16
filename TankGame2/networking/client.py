import socket
import threading
from . import protocol, vc_client



class Client:
    def __init__(self):
        self.server_ip = '127.0.0.1'
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

        # a queue that holds data from the server
        self.buffer = []

    def connect_tcp(self):
        self.server_socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server_socket_tcp.connect((self.server_ip, self.server_port_tcp))
        except ConnectionRefusedError:
            self.offline_mode = True

        if not self.offline_mode:
            self.running_tcp = True
            listening_thread = threading.Thread(target=self.listen_tcp, daemon=True)
            listening_thread.start()

    def connect_udp(self):
        self.running_udp = True
        self.server_socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(self.own_port + 1)
        self.server_socket_udp.bind(("0.0.0.0", self.own_port + 1))

        self.server_port_udp = self.server_port_tcp + self.lobby_id
        self.server_socket_udp.sendto("R".encode(), (self.server_ip, self.server_port_udp))

        listening_thread = threading.Thread(target=self.listen_udp, daemon=True)
        listening_thread.start()

    def disconnect_udp(self):
        self.running_udp = False
        if self.server_socket_udp is not None:
            self.server_socket_udp.close()

    def listen_tcp(self):
        while self.running_tcp:

            data = self.server_socket_tcp.recv(1024)
            print(data.decode())

            # push data to the buffer
            self.buffer.append(data.decode())

    def listen_udp(self):
        try:
            while self.running_udp:
                data, addr = self.server_socket_udp.recvfrom(1024)
                # print(data.decode())

                if addr == (self.server_ip, self.server_port_udp):
                    # push data to the buffer
                    self.buffer.append(data.decode())
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
        if self.server_socket_tcp is not None:
            self.server_socket_tcp.send(data.encode())
        else:
            print("no server found")

    def send_player_status(self, data):
        if self.server_socket_udp is not None:
            self.server_socket_udp.sendto(f"{self.name}|{data}".encode(), (self.server_ip, self.server_port_udp))

    # get the username of the owner of the current lobby
    def get_owner(self, raw=False):
        for user in self.user_list[0] + self.user_list[1]:
            if user.owner:
                if raw:
                    return user
                return user.name
        return None

    def get_this(self):
        for user in self.user_list[0] + self.user_list[1]:
            if user.name == self.name:
                return user
        # handle practice mode
        if len(self.user_list[0] + self.user_list[1]) == 0:
            return protocol.User(self.name, 1)

    def update_lobby(self, data):
        data = data.split("|")
        self.lobby_id = int(data[0][1])

        # get list
        if data[1] == "list":
            # update user lists
            self.user_list = [[], []]
            for string in data[2:]:
                self.user_list[int(string[0]) - 1].append(protocol.User(string[1:], int(string[0])))
        # add a player
        elif data[1] == "join":
            # add new user
            team = int(data[3]) - 1
            self.user_list[team].append(protocol.User(data[2], team))
        elif data[1] == "leave":
            # remove user
            for t in range(2):
                for user in self.user_list[t]:
                    if user.name == data[2]:
                        self.user_list[t].remove(user)
                        break
        elif data[1] == "promote":
            for user in self.user_list[0] + self.user_list[1]:
                # promote new owner (also demote old one)
                user.owner = user.name == data[2]


    def can_start(self):
        return self.get_owner() == self.name and len(self.user_list[0]) > 0 and len(self.user_list[1]) > 0


    def start_voice_client(self):
        self.vcclient = vc_client.VoiceChatClient(self.lobby_id, self.own_port)
        self.vcclient.start()

    def stop_voice_client(self):
        self.vcclient.running = False
        self.vcclient.client_socket.close()

