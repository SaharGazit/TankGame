import socket
import random
import threading

rendezvous = ('13.53.193.228', 50000)

# TODO: send Keep-Alive packets

HOST = "0.0.0.0"
# HOST = f"127.0.0.{random.randint(1, 100)}"

# get other peer connection details (address, port) from the rendezvous server
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, 50500+random.randint(1, 100)))
    sock.sendto("hello".encode(), rendezvous)

    data = []
    print("* Waiting for data from the server")
    while True:
        data = sock.recvfrom(1024)[0].decode().split(';')
        if len(data) == 3:
            print("Data:", data)
            break

    peer_addr, peer_port, own_port = data
    peer_port = int(peer_port)
    own_port = int(own_port)

    peer = (peer_addr, peer_port)


# hole punching
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, own_port))
    print("Punching hole")

    sock.sendto("punching hole".encode(), peer)


# receive messages from peer in another thread
def recv_msgs():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((HOST, own_port))
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"Peer: {data.decode()}\n> ")


recv_msgs_thread = threading.Thread(target=recv_msgs)
recv_msgs_thread.start()


# send udp messages
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    # when sending UDP packets, bind to the other peer port
    sock.bind((HOST, peer_port))

    while True:
        msg = input("> ")
        sock.sendto(msg.encode('utf-8'), peer)


# https: // docs.aws.amazon.com / AWSEC2 / latest / UserGuide / ec2 - instance - lifecycle.html
# a

