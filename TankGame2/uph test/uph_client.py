import socket
import random
import threading

# insert ec2 instance ip here. 127.0.0.1 if the server runs on this PC.
rendezvous = ('13.60.20.4', 50000)

GLOBAL_HOST = "0.0.0.0"
LOCAL_HOST = f"127.0.0.{random.randint(1, 100)}"
HOST = ""
LOCAL_ADDRESS = socket.gethostbyname(socket.gethostname())

mode = ""
while True:
    try:
        mode = input("Choose Mode: (DEBUG/LAN):\n").lower()
        if mode == "debug" or mode == "lan":
            HOST = GLOBAL_HOST
            break
        if mode == "loopback":
            HOST = LOCAL_HOST
            break

    finally:
        pass
    print("Invalid mode")

# get other peer connection details (address, port) from the rendezvous server
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    sock.bind((HOST, 50500+random.randint(1, 100)))
    if mode == "lan":
        sock.sendto((mode + ";" + socket.gethostbyname(socket.gethostname())).encode(), rendezvous)
    elif mode == "debug":
        sock.sendto((mode + ";" + LOCAL_HOST).encode(), rendezvous)

    data = []
    print("* Waiting for data from the server")
    while True:
        data = sock.recvfrom(1024)[0].decode().split(';')
        if data[0] == "not compatible":
            print("Rejected")
            i = 1 / 0  # temp crash until i add classes
            break
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

    print("1)")
    print(peer)
    sock.sendto("punching hole".encode(), peer)


# receive messages from peer in another thread
def recv_msgs():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print("2)")
        print((HOST, own_port))
        sock.bind((HOST, own_port))
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"Peer: {data.decode()}\n> ")


recv_msgs_thread = threading.Thread(target=recv_msgs)
recv_msgs_thread.start()


# send udp messages
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
    # when sending UDP packets, bind to the other peer port
    print("3)")
    print((HOST, peer_port))
    sock.bind((HOST, peer_port + 1))

    while True:
        msg = input("> ")
        sock.sendto(msg.encode('utf-8'), peer)


# https: // docs.aws.amazon.com / AWSEC2 / latest / UserGuide / ec2 - instance - lifecycle.html
