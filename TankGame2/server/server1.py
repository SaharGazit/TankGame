import protocol
from lobby import Lobby
import socket
import wonderwords
import select


class MainServer:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = protocol.server_port
        self.main_lobby = Lobby(0)  # players who haven't connected to a server yet (socket:User)
        self.lobbies = [self.main_lobby]  # all lobbies
        self.next_lobby_id = 1

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
                        user = protocol.User(addr=addr)
                        # temp: the server manually logins the user - this will be done until I start working on the databases
                        random_name = r.word(include_parts_of_speech=["noun"], word_min_length=3, word_max_length=8)
                        user.login(random_name)

                        # accept client
                        self.main_lobby.add_player(user, conn)
                        print(f"Accepted Connection from {addr} as {random_name}")

                        # send the player their details
                        conn.sendall(f"{user.name}|{user.address[1]}".encode())

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
                            self.lobbies.append(Lobby(self.next_lobby_id))
                            print(f"{user.name} has created lobby {self.lobbies[-1].id}")
                            self.next_lobby_id += 1

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
                            target_lobby = self.get_lobby_by_id(int(data[-1]))
                            if target_lobby is not None:
                                if len(target_lobby.users) != protocol.MAX_PLAYERS_IN_LOBBY:
                                    # add user to the lobby
                                    self.move_user(sock, self.main_lobby, target_lobby)
                                # bring player back to the title screen, if the server is full or if it doesn't exist
                                else:
                                    sock.sendall("kick".encode())
                            else:
                                print("aaa")
                                sock.sendall("kick".encode())
                        # lobby's owner wants to start or cancel its game
                        elif data == "start":
                            lobby.start_cooldown()
                        elif data == "cancel":
                            lobby.cancel_cooldown()
                        # handle game events
                        elif data[0] == "E":
                            lobby.broadcast(data + "|" + user.name, sock)

                # disconnect users not responding
                except ConnectionResetError:
                    self.disconnect_user(sock)

            # delete empty lobbies
            for lobby in self.lobbies[1:]:
                if len(lobby.users) == 0:
                    print(f"Lobby {lobby.id} has closed")
                    lobby.game_server.running = False
                    self.lobbies.remove(lobby)

    def get_lobby_list(self):
        # form lobby list string
        ll = ""
        for lobby in self.lobbies[1:]:
            if not lobby.game_server.game_started and len(lobby.users) < protocol.MAX_PLAYERS_IN_LOBBY:
                ll += f"{lobby.id}|{lobby.get_owner_name()}|{len(lobby.users)}||"

        # return no-lobbies if no available lobbies exist
        if ll == "":
            return "no-lobbies"
        else:
            return ll[:-2]

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
