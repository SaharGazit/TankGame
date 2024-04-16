import socket
import select
import wonderwords


class MainServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 31410
        self.main_lobby = Lobby(0)  # players who haven't connected to a server yet (socket:User)
        self.lobbies = [self.main_lobby]

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
            sockets, _, _ = select.select(
                [self.server_socket] + [sock for lobby in self.lobbies for sock in lobby.users.keys()], [], [])
            for sock in sockets:
                try:
                    # check if the new client is already connected or not
                    if sock == self.server_socket:
                        # handle new connection
                        conn, addr = self.server_socket.accept()

                        # create a user object
                        user = User()
                        # temp: the server manually logins the user - this will be done until I start working on the databases
                        random_name = r.word(include_parts_of_speech=["noun"], word_min_length=3, word_max_length=8)
                        user.login(random_name)
                        # accept client
                        self.main_lobby.add_player(user, conn)
                        print(f"Accepted Connection from {addr} as {random_name}")

                        # send the player their details
                        conn.sendall(user.name.encode())

                    else:
                        # identify user and lobby
                        user = None
                        lobby = None
                        for lo in self.lobbies:
                            if sock in lo.users:
                                user = lo.users[sock]
                                lobby = lo
                                break
                        # get data
                        data = sock.recv(1024).decode()

                        # client declared it is hosting a lobby
                        if data == "host":
                            # add a new lobby
                            self.lobbies.append(Lobby(self.get_new_id()))
                            print(f"{user.name} has created lobby {self.lobbies[-1].id}")

                            # add user to the lobby
                            self.move_user(sock, self.main_lobby, self.lobbies[-1])
                        # client declared it left its lobby
                        if data == "main":
                            # move user out of the lobby
                            self.move_user(sock, lobby, self.main_lobby)

                # disconnect users not responding
                except ConnectionResetError:
                    self.disconnect_user(sock)
                except OSError:
                    self.disconnect_user(sock)

            # delete empty lobbies
            for lobby in self.lobbies[1:]:
                if len(lobby.users) == 0:
                    print(f"Lobby {lobby.id} has closed")
                    self.lobbies.remove(lobby)

    def get_lobby_list(self):
        pass

    def get_new_id(self):
        possible_id = 1
        while True:
            if possible_id in [lobby.id for lobby in self.lobbies[1:]]:
                possible_id += 1
            else:
                break
        return possible_id


    @staticmethod
    def move_user(sock, from_, to):
        user = from_.users[sock]
        from_.remove_player(sock)
        to.add_player(user, sock)

    # remove disconnected player
    def disconnect_user(self, sock):
        sock.close()
        for lobby in self.lobbies:
            if sock in lobby.users.keys():
                name = lobby.users[sock].name
                lobby.remove_player(sock)
                print(f"{name} disconnected")
                break


class Lobby:
    def __init__(self, lobby_id):
        self.id = lobby_id
        self.users = {}

    def add_player(self, player, sock):
        self.users[sock] = player
        player.join_lobby(self)

        if self.id != 0:
            print(f"{player.name} joined lobby {self.id}")
            # broadcast new lobby status
            self.broadcast_status()

    def remove_player(self, sock):
        name = self.users[sock].name
        del self.users[sock]

        if self.id != 0:
            print(f"{name} left lobby {self.id}")
            # broadcast new lobby status
            self.broadcast_status()

    def broadcast_status(self):
        self.broadcast(f"L{self.id}{self.get_names_string()}")

    def broadcast(self, data):
        for sock in self.users.keys():
            sock.sendall(data.encode())

    def get_names_string(self):
        names_string = ""
        for user in self.users.values():
            names_string += "|" + user.name
            if user.owner:
                names_string += "#"
        return names_string


class User:
    def __init__(self):  # no socket, since it's already a part of a dictionary
        self.logged = False
        self.name = "guest"

        self.lobby_id = 0  # lobby id 0 means no lobby
        self.team = None
        self.owner = False

    def login(self, username):
        self.name = username
        self.logged = True

    def join_lobby(self, lobby):
        self.lobby_id = lobby.id
        if len(lobby.users) == 1:
            self.owner = True

        # TODO: set team


if __name__ == "__main__":
    main_server = MainServer()
    main_server.main()
