import socket
#  TODO: import "client" from main server


class VoiceServer:
    HOST = "0.0.0.0"
    PORT = 51410

    LOBBY_CAPACITY = 8

    def __init__(self, team1, team2):
        self.team_chat1 = team1
        self.team_chat2 = team2


    def start_server(self):
        pass



if __name__ == "__main__":
    vs = VoiceServer([('127.0.0.1', 10000)], ['127.0.0.1', 12000])
    vs.start_server()
