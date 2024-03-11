import socket
import random
import threading
import time


class Client:
    # insert ec2 instance ip here. 127.0.0.1 if the server runs on this PC.
    RENDEZVOUS = ('127.0.0.1', 50000)

    def __init__(self, mod, title):
        self.host = "0.0.0.0"
        self.port = 0  # client port
        self.peer = ()

        self.is_dm = None
        self.rps_result = None

        self.mod = mod
        self.program = title

        self.peer_socket_send = None
        self.peer_socket_recv = None
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

            elif self.program.error_code == 0:
                # create peer socket for sending and receiving
                self.peer_socket_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.peer_socket_send.bind((self.host, self.peer[1] + 1))
                self.peer_socket_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.peer_socket_recv.bind((self.host, self.port))

                # create a thread for listening
                recv_msgs_thread = threading.Thread(target=self.receive_data(), daemon=True)
                recv_msgs_thread.start()

                # rock scissors papers game (view: protocol.py)
                while self.is_dm is None:
                    print("aaa")
                    # send and receive guess
                    my_guess = random.randrange(3)
                    self.send_data(my_guess)

                    # wait for rps result
                    while self.rps_result is None:
                        pass

                    print("my guess: " + str(my_guess))
                    print("opponent's guess: " + str(self.rps_result))
                    # tie
                    if my_guess == self.rps_result:
                        self.rps_result = None
                    # win or lose
                    else:
                        self.is_dm = (my_guess, self.rps_result) in [(0, 2), (1, 0), (2, 1)]

                print(self.is_dm)

    def receive_data(self):
        print("aaaaa")
        while True:
            # get data
            data2, addr = self.peer_socket_recv.recvfrom(1024)
            data2 = data2.decode()
            print("Received " + data2 + " from the peer")

            # determine which status is the client in
            if self.is_dm is None:
                # get rps result
                self.rps_result = int(data2)
            else:
                print("idk wat to do wit it fam")

    # send data to the peer, called from main game
    def send_data(self, data):
        data = str(data)
        # send udp messages
        self.peer_socket_send.sendto(data.encode(), self.peer)

    # only required during online communication
    def punch_hole(self):
        # hole punching
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind((self.host, self.port))
            print("Punching hole")

            sock.sendto("punching hole".encode(), self.peer)
