import socket

HOST = '0.0.0.0'
PORT = 50000

# open server socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPServerSocket:
    peers = []  # list of 2 clients
    modes = []
    peers_local = []
    UDPServerSocket.bind((HOST, PORT))
    print("[!] Server is activated")

    while True:
        # add new client
        data = UDPServerSocket.recvfrom(1024)

        # handle the communication mode and the local ip
        extra_data = data[0].decode().split(";")
        modes.append(extra_data[0])
        peers_local.append(extra_data[1])

        addr, port = data[1]
        peers.append((addr, port))
        print(f"[+] Connection from {addr}:{port}")

        # when 2 clients are connected, start trading info
        if len(peers) == 2:
            addr1, port1 = peers.pop()
            addr2, port2 = peers.pop()
            if modes[0] == modes[1]:
                if modes[0] == "debug":
                    print(peers_local)
                    UDPServerSocket.sendto(f"{peers_local[0]};{port2 + 5};{PORT + 5}".encode(), (addr1, port1))
                    UDPServerSocket.sendto(f"{peers_local[1]};{PORT + 5};{port2 + 5}".encode(), (addr2, port2))
                if modes[0] == "lan":
                    print(peers_local)
                    UDPServerSocket.sendto(f"{peers_local[0]};{port2 + 5};{PORT + 5}".encode(), (addr1, port1))
                    UDPServerSocket.sendto(f"{peers_local[1]};{PORT + 5};{port2 + 5}".encode(), (addr2, port2))
                elif modes[0] == "internet" or modes[0] == "loopback":
                    UDPServerSocket.sendto(f"{addr2};{port2 + 5};{PORT + 5}".encode(), (addr1, port1))
                    UDPServerSocket.sendto(f"{addr1};{PORT + 5};{port2 + 5}".encode(), (addr2, port2))

                print("[!] Connected two clients, shutting down server")
            else:
                UDPServerSocket.sendto(f"not compatible".encode(), (addr1, port1))
                UDPServerSocket.sendto(f"not compatible".encode(), (addr2, port2))
                print("[!] Rejected two clients, shutting down server")

            break
