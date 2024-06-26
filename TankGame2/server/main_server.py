import protocol
from lobby import Lobby
import socket
import select
from pymongo import MongoClient
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Random import get_random_bytes


class MainServer:
    # database cluster at https://cloud.mongodb.com/v2/6651df10ac34d407537687c6#/metrics/replicaSet/6651e3235035b8486c814035/explorer/game/users/find
    cluster = "mongodb+srv://sahargazit:MONGOCLAT@cluster0.dtxvb6d.mongodb.net/game?retryWrites=true&w=majority&appName=Cluster0"

    def __init__(self):
        # server key
        self.aes_key = get_random_bytes(16)

        self.host = '0.0.0.0'
        self.port = protocol.server_port
        self.main_lobby = Lobby(0, self.aes_key)  # players who haven't connected to a server yet (socket:User)
        self.lobbies = [self.main_lobby]  # all lobbies
        self.next_lobby_id = 1

        # tcp socket for handling the main stage
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

        # mongodb client
        client = MongoClient(MainServer.cluster)
        self.userbase = client.game.users

    def main(self):
        print("Server started on {}:{}".format(self.host, self.port))

        # reset all users "logged" variable to false, in case the server shut down unexpectedly last time
        logged = self.userbase.find({"logged": True})
        for user in logged:
            self.userbase.update_one({"username": user["username"]}, {"$set": {"logged": False}})

        # listen for incoming connections
        self.server_socket.listen()

        running = True
        while running:
            # use select to wait for incoming connections or data from existing connections
            sockets, _, _ = select.select([self.server_socket] + [sock for lobby in self.lobbies for sock in lobby.users.keys()], [], [])
            for sock in sockets:
                try:
                    # check if the new client is already connected or not
                    if sock == self.server_socket:
                        # handle new connection
                        conn, addr = self.server_socket.accept()

                        # create a user object
                        user = protocol.User("guest", addr=addr)

                        # accept client
                        self.main_lobby.add_player(user, conn)
                        print(f"Accepted Connection from {addr}")

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
                        data = protocol.receive_data(sock)

                        if user.authenticated:
                            # decrypt and decode message
                            data = protocol.decrypt_data(self.aes_key, data).decode()

                            # client declared it is hosting a lobby
                            if data == "host":
                                # add a new lobby
                                self.lobbies.append(Lobby(self.next_lobby_id, self.aes_key))
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
                                self.send_data(self.get_lobby_list(), sock)
                            # client declared it joins a lobby
                            elif data[:-1] == "join":
                                target_lobby = self.get_lobby_by_id(int(data[-1]))
                                if target_lobby is not None:
                                    if len(target_lobby.users) != protocol.MAX_PLAYERS_IN_LOBBY:
                                        # add user to the lobby
                                        self.move_user(sock, self.main_lobby, target_lobby)
                                    # bring player back to the title screen, if the server is full or if it doesn't exist
                                    else:
                                        self.send_data("kick", sock)
                                else:
                                    self.send_data("kick", sock)
                            # lobby's owner wants to start or cancel its game
                            elif data == "start":
                                lobby.start_cooldown()
                            elif data == "cancel":
                                lobby.cancel_cooldown()
                            # user logged out
                            elif data == "logout":
                                print(f"{user.address} logged out from {data[1]}")
                                self.userbase.update_one({"username": user.name}, {"$set": {"logged": False}})
                                user.logout()
                            # handle game events
                            elif data[0] == "E":
                                lobby.broadcast(data + "|" + user.name, sock)
                            else:
                                data = data.split("|")
                                result = ""
                                # handle account
                                if data[0] == "login":
                                    credentials = {"username": data[1], "password": data[2]}
                                    result = self.login_user(credentials, user)
                                    if result == "success":
                                        print(f"{user.address} logged as {data[1]}")
                                        user.login(data[1])
                                elif data[0] == "signup":
                                    credentials = {"username": data[1], "password": data[2], "logged": False}
                                    result = self.signup_user(credentials)
                                self.send_data(result, sock)

                        else:
                            # get key
                            client_public_key = RSA.import_key(data)
                            encrypted_aes_key = self.encrypt_aes_key(client_public_key)
                            protocol.send_data(encrypted_aes_key, sock)
                            user.authenticated = True

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
                self.userbase.update_one({"username": name}, {"$set": {"logged": False}})
                break

    def get_lobby_by_id(self, id_):
        for lobby in self.lobbies[1:]:
            if lobby.id == id_:
                return lobby

    def login_user(self, credentials, user):
        the_user = self.find__user_in_database(credentials)
        if the_user is None:
            return "invalid|2"  # code for "invalid username/password"
        elif the_user["password"] == credentials["password"]:
            if the_user["logged"]:
                return "invalid|3"  # code for "account already online"
            else:
                user.login(the_user["username"])
                # change logged status to true
                self.userbase.update_one({"username": the_user["username"]}, {"$set": {"logged": True}})
                return "success"
        else:
            return "invalid|2"  # code for "incorrect username/password"

    def signup_user(self, credentials):
        if self.find__user_in_database(credentials) is None:
            self.userbase.insert_one(credentials)
            return "success"
        else:
            return "invalid|1"  # code for "username already exists"

    def find__user_in_database(self, user):
        return self.userbase.find_one({"username": user["username"]})

    def encrypt_aes_key(self, client_key):
        cipher_rsa = PKCS1_OAEP.new(client_key)
        encrypted_aes_key = cipher_rsa.encrypt(self.aes_key)
        return encrypted_aes_key

    def send_data(self, data, sock):
        data = protocol.encrypt_data(self.aes_key, data.encode())
        protocol.send_data(data, sock)