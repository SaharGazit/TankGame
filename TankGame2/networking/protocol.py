
main_port = 31410


class User:
    def __init__(self):  # no socket, since it's already a part of a dictionary
        self.logged = False
        self.name = "guest"

        self.team = 0
        self.owner = False

    def login(self, username):
        self.name = username
        self.logged = True
