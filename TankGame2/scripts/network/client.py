import socket

# insert ec2 instance ip here. 127.0.0.1 if the server runs on this PC.
RENDEZVOUS = ('13.51.163.196', 50000)


class Client:
    def __init__(self, mod):
        if mod == "debug":
            self.host = "127.0.0.1"

