import socket

server_ip = "127.0.0.1"
server_port = 30000
vcserver_port = 40000
MAX_PLAYERS_IN_LOBBY = 8

BYTE_CHUNK = 2024
VC_BYTE_CHUNK = 4096
AES_KEY = b'R\xc9\x1b\x08L\xe4M9\x83\xb0\x9a\x81\xa2J\xf4\xfa'


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
    if type(data) == str:
        data = data.encode()

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


