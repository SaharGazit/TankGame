import socket


class Server:
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 50000

    class Player:
        def __init__(self, con, mode, local_ip):
            self.ip = con[0]
            self.port = con[1]

            self.mode = mode
            self.local_ip = local_ip

    def main(self):
        # open server socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as UDPServerSocket:
            lobby = []  # list of clients
            UDPServerSocket.bind((self.host, self.port))
            print("[!] Server is activated")

            while True:
                # add new client
                data = UDPServerSocket.recvfrom(1024)
                extra_data = data[0].decode().split(";")
                client = self.Player(data[1], extra_data[0], extra_data[1])

                lobby.append(client)
                print(f"[+] Connection from {lobby[-1].ip}:{lobby[-1].port}")

                for player in lobby[:len(lobby) - 1]:
                    if player.mode == lobby[-1].mode:
                        peer1 = lobby.pop(lobby.index(player))
                        peer2 = lobby.pop()

                        if peer1.mode == "debug":
                            UDPServerSocket.sendto(f"{peer1.local_ip};{peer2.port + 5};{peer1.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.local_ip};{self.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))
                        elif peer1.mode == "lan":
                            UDPServerSocket.sendto(f"{peer1.local_ip};{peer2.port + 5};{self.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.local_ip};{self.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))
                        elif peer1.mode == "online":
                            UDPServerSocket.sendto(f"{peer2.ip};{peer2.port + 5};{self.port + 5}".encode(), (peer1.ip, peer1.port))
                            UDPServerSocket.sendto(f"{peer1.ip};{self.port + 5};{peer2.port + 5}".encode(), (peer2.ip, peer2.port))

                        print("[!] Connected two clients, shutting down server")
                        break


if __name__ == "__main__":
    server = Server()
    server.main()
