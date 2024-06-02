import socket
from voice_server import VoiceChatServer
import protocol
import threading
import random


class GameServer:

    def __init__(self, id_):
        self.host = "0.0.0.0"
        self.port = protocol.server_port + id_
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.settimeout(0.1)

        self.teams = [{}, {}]
        self.spawn_positions = [[(1000, 1000), (1100, 1000), (1200, 1000), (1300, 1000)], [(200, 200), (300, 200), (400, 200), (500, 200)]]

        self.vcserver = VoiceChatServer(id_)

        self.running = False
        self.game_started = False

    def start(self, users):
        vcs = {}
        for user in users.values():
            addr = (user.address[0], user.address[1] + 1)
            self.teams[user.team - 1][addr] = [user.name, False]
            vc_addr = (user.address[0], user.address[1])
            vcs[vc_addr] = user.name

        self.running = True
        listen_thread = threading.Thread(target=self.listen, daemon=True)
        listen_thread.start()

        self.vcserver.start(vcs)

    def stop(self):
        self.running = False
        self.teams = [{}, {}]
        self.spawn_positions = [[(1000, 1000), (1100, 1000)], [(200, 200), (300, 200), (400, 200), (500, 200)]]

        self.vcserver.stop()

    def listen(self):
        while self.running:
            try:
                data, addr = protocol.receive_data(self.server_socket)
                data = data.decode()
            except socket.timeout:
                continue
            except ConnectionResetError:
                continue

            # identify client
            team = -1
            for i in range(2):
                if addr in self.teams[i].keys():
                    team = i
                    self.game_started = True
                    break

            # ignore unwanted clients
            if team == -1:
                print(f"Rejected {addr}: They're not in the lobby")
                continue

            # check if it's the first contact of the client
            if not self.teams[team][addr][1]:
                self.teams[team][addr][1] = True

                # assign random position
                pos = self.spawn_positions[team][random.randrange(len(self.spawn_positions[team]))]
                self.spawn_positions[team].remove(pos)

                # send new player position
                protocol.send_data(f"{self.teams[team][addr][0]}|{pos[0]}|{pos[1]}", self.server_socket, addr)

            # handle client data
            else:
                self.broadcast("G|" + data, addr)

    def broadcast(self, data, exc=None):
        for team in range(2):
            for player in self.teams[team].keys():
                if self.teams[team][player][1] and player != exc:
                    protocol.send_data(data, self.server_socket, player)