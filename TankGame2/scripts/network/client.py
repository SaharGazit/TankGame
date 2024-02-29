import socket
import random


class Client:
    # insert ec2 instance ip here. 127.0.0.1 if the server runs on this PC.
    RENDEZVOUS = ('127.0.0.1', 50000)

    def __init__(self, mod):
        self.host = "0.0.0.0"

        # connect to rendezvous server
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, 50500 + random.randint(1, 100)))

            # send info to the server
            message = mod + ";"
            if mod == "debug":
                message += "127.0.0." + str(random.randint(1, 100))
                sock.sendto(message.encode(), Client.RENDEZVOUS)
                # TODO: LAN

            data = []
            # get data from the server
            while True:
                data = sock.recvfrom(1024)[0].decode().split(";")
                print("data: ", data)
                if len(data) == 3:
                    break

            peer_addr, peer_port, own_port = data
            peer_port = int(peer_port)
            own_port = int(own_port)
            self.peer = (peer_addr, peer_port)

        # hole punching



if __name__ == "__main__":
    test_client = Client('debug')


