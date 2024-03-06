import socket
import random
import threading


class Client:
    # insert ec2 instance ip here. 127.0.0.1 if the server runs on this PC.
    RENDEZVOUS = ('127.0.0.1', 50000)

    def __init__(self, mod, title):
        self.host = "0.0.0.0"
        self.port = 0  # client port
        self.peer = ()

        self.mod = mod
        self.program = title

        self.force_stop_queueing = False

        # connect to rendezvous server
        conn_init_thread = threading.Thread(target=self.connect_with_rendezvous, daemon=True)
        conn_init_thread.start()

    def connect_with_rendezvous(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, 50500 + random.randint(1, 100)))
            sock.settimeout(1)

            # send info to the server
            message = self.mod + ";"
            if self.mod == "debug":
                message += "127.0.0." + str(random.randint(1, 100))
                sock.sendto(message.encode(), Client.RENDEZVOUS)
                # TODO: LAN

            # get data from the server
            while not self.force_stop_queueing:
                try:
                    data = sock.recvfrom(1024)[0].decode().split(";")

                # set error code if socket address is wrong
                except ConnectionResetError:
                    self.program.error_code = 1
                    print("invalid rendezvous ip address")
                    break

                # check if the client canceled the queueing
                except socket.timeout:
                    continue

                print("data: ", data)
                if len(data) == 3:
                    # get peer
                    peer_addr, peer_port, own_port = data
                    self.port = int(own_port)
                    self.peer = (peer_addr, int(peer_port))
                    break

            # send cancel message to server
            if self.force_stop_queueing:
                sock.sendto("cancel".encode(), Client.RENDEZVOUS)

    def receive_data(self):

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
            sock.sendto(data.encode('utf-8'), self.peer)

    # only required during online communication
    def punch_hole(self):
        # hole punching
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            print("Punching hole")

            sock.sendto("punching hole".encode(), self.peer)
