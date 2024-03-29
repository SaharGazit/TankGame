import random
import socket
import pyaudio
import threading


class VoiceChatClient:
    # determines the size of each block of audio data that is processed at a time
    CHUNK = 1024
    # states how many samples of audio are played or captured every second. has to match with the server's rate
    RATE = 44100
    # the audio data's format. should stay pyaudio.paInt16 (16-bit signed integer format) as it is a common format for audio data
    FORMAT = pyaudio.paInt16
    # 1 - mono audio (all audio comes from a single channel) 2 - stereo audio (comes from multiple channels, like left and right)
    CHANNELS = 1

    def __init__(self):
        self.host = '127.0.0.1'  # server ip
        self.server_port = 31410

        # initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # create a UDP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('127.0.0.1', 40500 + random.randrange(1000)))

        self.stream = None

    def start_client(self):
        # open audio stream
        self.stream = self.audio.open(format=VoiceChatClient.FORMAT, channels=VoiceChatClient.CHANNELS,
                                      rate=VoiceChatClient.RATE, input=True, output=True,
                                      frames_per_buffer=VoiceChatClient.CHUNK)

        # start reading and writing threads
        write_thread = threading.Thread(target=self.write, daemon=True)
        write_thread.start()
        self.read()


    def read(self):
        while True:
            # read audio from this computer
            data = self.stream.read(VoiceChatClient.CHUNK)

            # send audio
            self.client_socket.sendto(data, (self.host, self.server_port))

    def write(self):
        while True:
            # get audio from server
            data, addr = self.client_socket.recvfrom(2048)

            # write audio (play it)
            self.stream.write(data)


if __name__ == "__main__":
    # create a test vc client
    vcc = VoiceChatClient()
    vcc.start_client()
