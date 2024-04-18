
main_port = 31410


class User:
    def __init__(self, name="guest", team=0):  # no socket, since it's already a part of a dictionary
        self.logged = name != "guest"

        if name[-1] == "#":
            name = name[:-1]
            self.owner = True
        else:
            self.owner = False

        self.name = name
        self.team = team

    def login(self, username):
        self.name = username
        self.logged = True
