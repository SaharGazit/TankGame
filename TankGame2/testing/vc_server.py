import socket
#  TODO: import "client" from main server


class VoiceServer:
    HOST = "0.0.0.0"
    PORT = 51410

    LOBBY_CAPACITY = 8

    def __init__(self):
        self.lobby = []

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((VoiceServer.HOST, VoiceServer.PORT))

    # this server temporary connects only two players and in a limited way
    def start_server(self):
        print("listening")
        while True:
            data, addr = self.socket.recvfrom(2048)
            if addr not in self.lobby:
                self.lobby.append(addr)
                print("added")

            for client_address in self.lobby:
                if client_address != addr:
                    self.socket.sendto(data, client_address)


if __name__ == "__main__":
    vs = VoiceServer()
    vs.start_server()
