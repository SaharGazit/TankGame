
main_port = 31410
MAX_PLAYERS_IN_LOBBY = 2


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

        self.distance_to_main = 0

    def login(self, username):
        self.name = username
        self.logged = True