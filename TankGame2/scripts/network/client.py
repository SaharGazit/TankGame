import socket
import random
import threading


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

            # get peer
            peer_addr, peer_port, own_port = data
            self.port = int(own_port)
            self.peer = (peer_addr, int(peer_port))

    def receive_data(self):
        # hole punching
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            print("Punching hole")

            sock.sendto("punching hole".encode(), self.peer)

        # receive data from the peer using another thread
        def recv_msgs():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock2:
                sock2.bind((self.host, self.port))
                while True:
                    data2, addr = sock2.recvfrom(1024)
                    print(f"Peer: " + data2.decode())
                    # TODO: stuff with the data

        recv_msgs_thread = threading.Thread(target=recv_msgs, daemon=True)
        recv_msgs_thread.start()

    # send data to the peer, called from main game
    def send_data(self, data):
        # send udp messages
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # when sending UDP packets, bind to the other peer port

            sock.bind((self.host, self.peer[1] + 1))

            while True:
                sock.sendto(data.encode('utf-8'), self.peer)


if __name__ == "__main__":
    test_client = Client('debug')


