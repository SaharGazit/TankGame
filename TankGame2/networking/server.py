import socket
import select
import wonderwords
import protocol


class MainServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = protocol.main_port
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
                        user = protocol.User()
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
                        elif data == "main":
                            # move user out of the lobby
                            self.move_user(sock, lobby, self.main_lobby)
                        # client requested lobby list
                        elif data == "list":
                            # return the list of lobbies
                            sock.sendall(self.get_lobby_list().encode())
                        # client declared it joins a lobby
                        elif data[:-1] == "join":
                            # add user to the lobby
                            self.move_user(sock, self.main_lobby, self.get_lobby_by_id(int(data[-1])))
                        # lobby's owner wants to start or cancel its game
                        elif data == "start":
                            lobby.broadcast("start")
                        elif data == "cancel":
                            lobby.broadcast("cancel")

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
        ll = ""
        for lobby in self.lobbies[1:]:
            ll += f"{lobby.id}|{lobby.get_owner_name()}|{len(lobby.users)}||"
        if ll == "":
            return "no-lobbies"
        else:
            return ll[:-2]

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

    def get_lobby_by_id(self, id_):
        for lobby in self.lobbies[1:]:
            if lobby.id == id_:
                return lobby


class Lobby:
    def __init__(self, lobby_id):
        self.id = lobby_id
        self.users = {}

    def add_player(self, player, sock):
        # add user to the lobby's users list
        self.users[sock] = player
        # if it is the first player in the lobby, give them owner
        if len(self.users) == 1:
            self.users[sock].owner = True

        if self.id != 0:
            # give the user a team
            team1_count = len([user for user in self.users.values() if user.team == 1])
            if team1_count <= len(self.users) - 1 - team1_count:
                player.team = 1
            else:
                player.team = 2
            print(f"{player.name} joined lobby {self.id}")
            # broadcast new lobby status
            self.broadcast_status()

    def remove_player(self, sock):
        user = self.users[sock]

        # reset user info
        user.team = 0
        if user.owner:
            user.owner = False
            # nominate new user as owner
            for user in self.users.values():
                if not user.owner:
                    user.owner = True
                    break

        # save name and remove the user from the user list
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
            names_string += "|" + str(user.team) + user.name
            if user.owner:
                names_string += "#"
        return names_string

    def get_owner_name(self):
        return [user.name for user in self.users.values() if user.owner][0]





if __name__ == "__main__":
    main_server = MainServer()
    main_server.main()
