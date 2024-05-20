from server2 import GameServer


class Lobby:
    def __init__(self, lobby_id):
        self.id = lobby_id
        self.users = {}

        self.countdown = False
        self.game_server = GameServer(self.id)


    def add_player(self, player, sock):
        # cancel cooldown
        if self.countdown:
            self.cancel_cooldown()

        # add user to the lobby's users list
        self.users[sock] = player
        # if it is the first player in the lobby, give them owner
        if len(self.users) == 1:
            self.users[sock].owner = True

        if self.id != 0:
            # assign the user a team
            team1_count = len([user for user in self.users.values() if user.team == 1])
            if team1_count <= len(self.users) - 1 - team1_count:
                player.team = 1
            else:
                player.team = 2
            print(f"{player.name} joined lobby {self.id}")
            # send lobby list to new player
            self.send_lobby_list(sock)
            # broadcast join
            self.broadcast(f"L{self.id}|join|{player.name}|{player.team}", sock)

    def remove_player(self, sock):
        user = self.users[sock]

        if user.owner:
            # nominate new user as owner
            for user2 in self.users.values():
                if not user2.owner:
                    user2.owner = True
                    # broadcast new owner (promote
                    self.broadcast(f"L{self.id}|promote|{user2.name}", sock)
                    break

            # remove user's owner
            user.owner = False

        # remove user from the user list
        del self.users[sock]
        # remove user from the game user list
        if self.game_server.game_started:
            if (user.address[0], user.address[1] + 1) in self.game_server.teams[user.team - 1].keys():
                del self.game_server.teams[user.team - 1][(user.address[0], user.address[1] + 1)]
        # reset team
        user.team = 0

        if self.id != 0:
            print(f"{user.name} left lobby {self.id}")
            # broadcast leave
            self.broadcast(f"L{self.id}|leave|{user.name}")

        # cancel cooldown
        if self.countdown and not self.game_server.game_started:
            self.cancel_cooldown()

    def send_lobby_list(self, sock):
        # get a string that contains all the names, teams and owner marks
        names_string = ""
        for user in self.users.values():
            names_string += "|" + str(user.team) + user.name
            if user.owner:
                names_string += "#"

        sock.sendall(f"L{self.id}|list{names_string}".encode())

    def broadcast(self, data, exc=None):
        for sock in self.users.keys():
            if sock != exc:
                sock.sendall(data.encode())

    def get_owner_name(self):
        return [user.name for user in self.users.values() if user.owner][0]

    def start_cooldown(self):
        self.countdown = True
        self.broadcast("start")
        self.game_server.start(self.users)

    def cancel_cooldown(self):
        self.countdown = False
        self.broadcast("cancel")
        self.game_server.stop()