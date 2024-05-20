server_ip = "127.0.0.1"
server_port = 30000
vcserver_port = 40000
MAX_PLAYERS_IN_LOBBY = 8


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

        self.volume_factor = 0

    def login(self, username):
        self.name = username
        self.logged = True

    hundred_radius = 200
    zero_radius = 600

    def set_volume_factor(self, distance_to_main):
        if distance_to_main < 200:
            self.volume_factor = 1
        elif distance_to_main <= 600:
            self.volume_factor = (600 - distance_to_main) / 400
        else:
            self.volume_factor = 0
