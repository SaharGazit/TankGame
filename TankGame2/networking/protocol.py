
main_port = 31410
spawn_positions = [[(1000, 1000), (1200, 1000)], [(200, 200), (400, 200)]]


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

    def login(self, username):
        self.name = username
        self.logged = True
