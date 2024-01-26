import socket

HOST = '0.0.0.0'
PORT = 50000

# open server socket
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPServerSocket:
    peers = []  # list of 2 clients
    UDPServerSocket.bind((HOST, PORT))
    print("[!] Server is activated")

    while True:
        # add new client
        addr, port = UDPServerSocket.recvfrom(1024)[1]
        peers.append((addr, port))
        print(f"[+] Connection from {addr}:{port}")

        # when 2 clients are connected, start trading info
        if len(peers) == 2:
            addr1, port1 = peers.pop()
            addr2, port2 = peers.pop()

            UDPServerSocket.sendto(f"{addr2};{port2 + 5};{PORT + 5}".encode('utf-8'), (addr1, port1))
            UDPServerSocket.sendto(f"{addr1};{PORT + 5};{port2 + 5}".encode('utf-8'), (addr2, port2))
            print("[!] Connected two clients, shutting down server")
            break
