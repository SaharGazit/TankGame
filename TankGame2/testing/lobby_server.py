import socket
import select


class LobbyServer:

    def __init__(self):
        self.host = '0.0.0.0'  # Server IP
        self.port = 31410  # Server port
        self.lobby = []
        self.MAX_CLIENTS = 8

        # tcp socket for handling the lobby stage
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))


    def start_server(self):
        print("Server started on {}:{}".format(self.host, self.port))

        # listen for incoming connections
        self.server_socket.listen()


        while True:
            # use select to wait for incoming connections or data from existing connections
            sockets, _, _ = select.select([self.server_socket] + [user.socket for user in self.lobby], [], [])

            for sock in sockets:
                # check if the new client is already in the lobby or not
                if sock == self.server_socket:
                    # handle new connection
                    conn, addr = self.server_socket.accept()
                    name = conn.recv(1024).decode()

                    # check if server is full
                    if len(self.lobby) == 8:
                        print("Rejected " + str(addr) + " because server is already full")
                        conn.close()

                    else:
                        print(f"Accepted connection from {addr}")
                        team = (len(self.lobby) % 2) + 1
                        self.lobby.append(User)

                else:
                    # get data
                    data = sock.recv(1024)
                    if data:
                        data = data.decode()
                        # TODO: HANDLE IT
                    else:
                        # kick player if he disconnected
                        sock.close()
                        self.lobby.remove(sock)
                        print(f"Connection from {sock.getpeername()} closed")


    # def get_user_index(self, addr):
    #     addr_list = [x.socket_address for x in self.lobby]
    #     if addr in addr_list:
    #         return self.lobby.index(addr)
    #     else:
    #         return -1


class User:
    def __init__(self, sock, username, _id, team):
        self.socket = sock
        self.username = username

        self.id = _id
        self.team = team


if __name__ == "__main__":
    main_server = LobbyServer()
    main_server.start_server()
