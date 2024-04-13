import socket

import select
import wonderwords


class MainServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 31410
        self.main_lobby = {}  # players who haven't connected to a server yet (socket:User)
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
            sockets, _, _ = select.select([self.server_socket] + [user_address for user_address in self.main_lobby.keys()], [], [])
            for sock in sockets:
                # check if the new client is already connected or not
                if sock == self.server_socket:
                    # handle new connection
                    conn, addr = self.server_socket.accept()

                    # create a user object
                    self.main_lobby[conn] = User()
                    # temp: the server manually logins the user - this will be done until I start working on the databases
                    self.main_lobby[conn].login(r.word(include_parts_of_speech=["noun"], word_min_length=3, word_max_length=8))
                    # accept client
                    print(f"Accepted Connection from {addr}")

                    # send the player their details
                    conn.sendall(self.main_lobby[conn].name.encode())

                else:
                    # identify user
                    user = self.main_lobby[sock]
                    try:
                        # get data
                        data = sock.recv(1024).decode()

                        # client requested to host a lobby
                        if data == "host":
                            # add a new lobby
                            self.lobbies.append(Lobby(len(self.lobbies)))
                            print(f"{user.name} has created a lobby")

                            # add player to the lobby
                            self.lobbies[-1].add_player(user)
                            sock.sendall(str(self.lobbies[-1].id).encode())

                    except ConnectionResetError:
                        # remove disconnected player
                        print(f"{user.name} disconnected")
                        self.disconnect_user(sock)


    def get_lobby_list(self):
        pass

    def disconnect_user(self, sock):
        sock.close()
        del self.main_lobby[sock]


class Lobby:
    def __init__(self, lobby_id):
        self.id = lobby_id
        self.players = []

    def add_player(self, player):
        if len(self.players) == 0:
            player.owner = True

        self.players.append(player)
        player.lobby_id = self.id


class User:
    def __init__(self):  # no socket, since it's already a part of a dictionary
        self.logged = False
        self.name = "guest"

        self.lobby_id = None
        self.team = None
        self.owner = False

    def login(self, username):
        self.name = username
        self.logged = True


    @staticmethod
    def get_name_list(user_dict):
        return "|".join([user.name for user in user_dict.values()])


if __name__ == "__main__":
    main_server = MainServer()
    main_server.main()
