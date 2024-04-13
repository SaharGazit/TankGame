import socket
import threading

import select
import wonderwords


class MainServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 31410
        self.players = {}  # players who haven't connected to a server yet (socket:User)
        self.lobbies = []

        # tcp socket for handling the main stage
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

    def main(self):
        print("Server started on {}:{}".format(self.host, self.port))

        # listen for incoming connections
        self.server_socket.listen()

        running = True
        r = wonderwords.RandomWord()
        while running:
            # use select to wait for incoming connections or data from existing connections
            sockets, _, _ = select.select([self.server_socket] + [user_address for user_address in self.players.keys()], [], [])
            for sock in sockets:
                # check if the new client is already connected or not
                if sock == self.server_socket:
                    # handle new connection
                    conn, addr = self.server_socket.accept()

                    # create a user object
                    self.players[conn] = User()
                    # temp: the server manually logins the user - this will be done until I start working on the databases
                    self.players[conn].login(r.word(include_parts_of_speech=["noun"], word_min_length=3, word_max_length=8))
                    # accept client
                    print(f"Accepted Connection from {addr}")

                    # send the player their details
                    conn.sendall(self.players[conn].name.encode())

                else:
                    # identify user
                    user = self.players[sock]
                    try:
                        # get data
                        data = sock.recv(1024).decode()

                        # client requested to host a lobby
                        if data == "host":
                            # lobbies should naturally be sorted by their ID's, so if an id is missing it should be replaced by a new lobby
                            new_lobby_id = len(self.lobbies)
                            for i in range(new_lobby_id):
                                if self.lobbies[i].id != i:
                                    new_lobby_id = i
                                    break
                            # place new lobby at the right position, and start it
                            self.lobbies = self.lobbies[:new_lobby_id] + [LobbyServer(new_lobby_id)] + self.lobbies[new_lobby_id:]
                            self.lobbies[new_lobby_id].thread.start()

                            print(f"{user.name} has created lobby number {new_lobby_id}")
                            sock.sendall(str(new_lobby_id).encode())

                    except ConnectionResetError:
                        # remove disconnected player
                        print(f"{user.name} disconnected")
                        self.disconnect_user(sock)


    def get_lobby_list(self):
        pass

    def disconnect_user(self, sock):
        sock.close()
        del self.players[sock]


class LobbyServer:

    def __init__(self, id_):
        self.id = id_
        self.thread = threading.Thread(target=self.start_server, daemon=True)

        self.host = '0.0.0.0'  # Server IP
        self.port = 31411 + self.id  # Server port
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
            for sock in sockets:
                # check if the client is already in the lobby or not
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
                        self.lobby[conn] = User()
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
                        self.disconnect_user(sock)
                        print(f"{user.name} disconnected")
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

    def get_player_count(self):
        return len(self.lobby)

    def disconnect_user(self, sock):
        sock.close()
        del self.lobby[sock]


class User:
    def __init__(self):  # no socket, since it's already a part of a dictionary
        self.logged = False
        self.name = "guest"

        self.id = None
        self.team = None

    def login(self, username):
        self.name = username
        self.logged = True

    @staticmethod
    def get_name_list(user_dict):
        return "|".join([user.name for user in user_dict.values()])



if __name__ == "__main__":
    main_server = MainServer()
    main_server.main()
