import socket

server_ip = "127.0.0.1"
server_port = 30000
vcserver_port = 40000
MAX_PLAYERS_IN_LOBBY = 8

BYTE_CHUNK = 1024
VC_BYTE_CHUNK = 4096

class User:
    def __init__(self, name="guest", team=0, addr=None):  # no socket, since it's already a part of a dictionary
        self.logged = name != "guest"

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

    hundred_radius = 200
    zero_radius = 600

    def set_volume_factor(self, distance_to_main):
        if distance_to_main < 200:
            self.volume_factor = 1
        elif distance_to_main <= 600:
            self.volume_factor = (600 - distance_to_main) / 400
        else:
            self.volume_factor = 0


def send_data(data, sock, addr=None):
    sock_type = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
    if sock_type == socket.SOCK_STREAM:
        sock.sendall(data.encode())
    elif sock_type == socket.SOCK_DGRAM:
        if type(data) == str:
            data = data.encode()
        sock.sendto(data, addr)


def receive_data(sock, vc=False):
    sock_type = sock.getsockopt(socket.SOL_SOCKET, socket.SO_TYPE)
    data = ""
    if sock_type == socket.SOCK_STREAM:
        data = sock.recv(BYTE_CHUNK).decode()

    elif sock_type == socket.SOCK_DGRAM:
        if vc:
            data = sock.recvfrom(VC_BYTE_CHUNK)
        else:
            data = sock.recvfrom(BYTE_CHUNK)
            data = (data[0].decode(), data[1])

    return data
