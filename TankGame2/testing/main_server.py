import socket


class MainServer:

    def __init__(self):
        self.host = '0.0.0.0'  # Server IP
        self.port = 31410  # Server port
        self.lobby = []
        self.MAX_CLIENTS = 8
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))

    def start_server(self):
        print("Server started on {}:{}".format(self.host, self.port))

        while True:
            # get data from a user
            data, addr = self.server_socket.recvfrom(1024)
            data = data.decode()

            # identify user
            user_index = self.get_user_index(addr)
            # handle new user
            if user_index == -1:
                if ";" in data:
                    data = data.split(";")
                    team = (len(self.lobby) % 2) + 1
                    self.lobby.append(User(addr, data[0], len(self.lobby), team))
                    print(f"User")

                # throw unrelated requests
                else:
                    print(f"Invalid request from {addr}.\nData: {data}")

    def get_user_index(self, addr):
        addr_list = [x.socket_address for x in self.lobby]
        if addr in addr_list:
            return self.lobby.index(addr)
        else:
            return -1


class User:
    def __init__(self, sa, username, _id, team):
        self.socket_address = sa
        self.username = username

        self.id = _id
        self.team = team


