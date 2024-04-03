import socket
import select


class LobbyServer:

    def __init__(self):
        self.host = '0.0.0.0'  # Server IP
        self.port = 31410  # Server port
        self.lobby = {}
        self.MAX_CLIENTS = 8

        # tcp socket for handling the lobby stage
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def start_server(self):
        print("Server started on {}:{}".format(self.host, self.port))

        # listen for incoming connections
        self.server_socket.listen()

        running = True
        while running:
            # use select to wait for incoming connections or data from existing connections
            sockets, _, _ = select.select([self.server_socket] + [user_address for user_address in self.lobby.keys()], [], [])
            print(sockets)
            for sock in sockets:
                # check if the new client is already in the lobby or not
                if sock == self.server_socket:
                    # handle new connection
                    conn, addr = self.server_socket.accept()
                    name = conn.recv(1024).decode()
                    # TODO: later there has to be some kind of authentication here. not everyone who logins here as "Sahar05" is Sahar05.

                    lobby_player_count = len(self.lobby)
                    # check if server is full
                    if lobby_player_count == 8:
                        # reject client if server is full
                        print("Rejected " + str(addr) + " because server is already full")
                        conn.close()
                    else:
                        # accept client
                        print(f"Accepted connection from {addr}")
                        team = (lobby_player_count % 2) + 1
                        self.lobby[conn] = User(name, lobby_player_count, team)
                        # update lobby for other clients
                        self.broadcast(User.get_name_list(self.lobby))

                else:
                    # get data
                    data = sock.recv(1024)
                    # identify user
                    user = self.lobby[sock]

                    if data:
                        # handle data
                        data = data.decode()
                        if data == "start":
                            # start the game
                            self.start_server()
                            running = False
                    else:
                        # remove disconnected player
                        sock.close()
                        print(f"{user.name} disconnected")
                        del self.lobby[sock]
                        # update lobby for other clients
                        self.broadcast(User.get_name_list(self.lobby))

    def start_game(self):
        # TODO: broadcast the game-server port instead of t
        self.broadcast("t")
        for client in self.lobby.keys():
            client.close()

    def broadcast(self, data, broadcaster=None):
        for client in self.lobby.keys():
            if client != broadcaster:
                client.sendall(data.encode())


class User:
    def __init__(self, username, _id, team):  # no socket since it's already a part of a dictionary
        self.name = username

        self.id = _id
        self.team = team

    @staticmethod
    def get_name_list(user_dict):
        return "|".join([user.name for user in user_dict.values()])


if __name__ == "__main__":
    main_server = LobbyServer()
    main_server.start_server()
