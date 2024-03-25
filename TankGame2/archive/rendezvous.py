import socket


class Server:
    def __init__(self):
        self.host = '127.0.0.2'
        self.port = 50000

    class Player:
        def __init__(self, con, mod, local_ip):
            self.ip = con[0]
            self.port = con[1]

            self.mod = mod
            self.local_ip = local_ip

    def main(self):
        # open server socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPServerSocket:
            lobby = []  # list of clients
            UDPServerSocket.bind((self.host, self.port))
            print("[!] Server is activated")

            while True:
                # get data
                data = UDPServerSocket.recvfrom(1024)

                # check if player is already in lobby
                if data[1] in [(i.ip, i.port) for i in lobby]:
                    # remove the client which is requesting to cancel the queue
                    if data[0].decode() == "cancel":
                        lobby.pop([(i.ip, i.port) for i in lobby].index(data[1]))
                        print(f"[-] Disconnected {data[1]} from lobby (reason: client request)")
                    continue

                else:
                    extra_data = data[0].decode().split(";")
                    print(extra_data)
                    client = self.Player(data[1], extra_data[0], extra_data[1])

                    lobby.append(client)
                    print(f"[+] Connection from {lobby[-1].ip}:{lobby[-1].port}")

                for player in lobby[:len(lobby) - 1]:
                    if player.mod == lobby[-1].mod:
                        peer1 = lobby.pop(lobby.index(player))
                        peer2 = lobby.pop()

                        if peer1.mod == "debug":
                            print(f"{peer2.local_ip};{peer2.port + 5};{peer1.port + 5}")
                            print(f"{peer1.local_ip};{peer1.port + 5};{peer2.port + 5}")
                            UDPServerSocket.sendto(f"{peer2.local_ip};{peer2.port + 5};{peer1.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.local_ip};{peer1.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))
                        elif peer1.mod == "lan":
                            UDPServerSocket.sendto(f"{peer2.local_ip};{peer2.port + 5};{self.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.local_ip};{self.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))
                        elif peer1.mod == "online":
                            UDPServerSocket.sendto(f"{peer2.ip};{peer2.port + 5};{self.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.ip};{self.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))

                        print("[!] Connected two clients")


if __name__ == "__main__":
    server = Server()
    server.main()

# TODO: this python file is nominated to be deleted
