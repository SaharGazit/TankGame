import socket


class VoiceChatServer:
    def __init__(self):
        self.host = '0.0.0.0'  # Server IP
        self.port = 31410  # Server port
        self.clients = []
        self.MAX_CLIENTS = 8
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        print("Server started on {}:{}".format(self.host, self.port))

        while True:
            data, client_address = self.server_socket.recvfrom(4096)
            if client_address not in self.clients:
                if len(self.clients) < self.MAX_CLIENTS:
                    self.clients.append(client_address)
                    print("Client {} connected".format(client_address))
                else:
                    print("Connection refused. Maximum clients reached.")
            else:
                # add client index to the message
                data = f"{self.clients.index(client_address)}".encode() + data

                self.broadcast(data, client_address)

    def broadcast(self, data, sender_address):
        for client_address in self.clients:
            if client_address != sender_address:
                self.server_socket.sendto(data, client_address)
            elif len(self.clients) == 1:
                self.server_socket.sendto("empty".encode(), sender_address)


if __name__ == "__main__":
    server = VoiceChatServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server Stopped")
