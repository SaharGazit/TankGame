import socket
import pyaudio
import threading
from . import protocol
import numpy


class VoiceChatClient:
    # determines the size of each block of audio data that is processed at a time
    CHUNK = 2024
    # states how many samples of audio are played or captured every second
    RATE = 44100
    # the audio data's format. should stay pyaudio.paInt16 (16-bit signed integer format) as it is a common format for audio data
    FORMAT = pyaudio.paInt16
    # 1 - mono audio (all audio comes from a single channel) 2 - stereo audio (comes from multiple channels, like left and right)
    CHANNELS = 1

    def __init__(self, lobby_id, port):
        self.host = protocol.server_ip
        self.server_port = protocol.vcserver_port + lobby_id

        # initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # create a UDP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', port + 2))
        self.client_socket.settimeout(1)

        self.running = False
        self.read_stream = None
        self.write_streams = {}

    def start(self, users):
        self.running = True
        # open audio stream
        self.read_stream = self.audio.open(format=VoiceChatClient.FORMAT, channels=VoiceChatClient.CHANNELS,
                                           rate=VoiceChatClient.RATE, input=True,
                                           frames_per_buffer=VoiceChatClient.CHUNK)

        # open write thread
        write_thread = threading.Thread(target=self.create_stream, daemon=True)
        write_thread.start()

        # reset streams
        self.write_streams = {}
        for user in users:
            print(user.name)
            self.write_streams[user] = self.audio.open(format=VoiceChatClient.FORMAT,
                                                       channels=VoiceChatClient.CHANNELS,
                                                       rate=VoiceChatClient.RATE, output=True,
                                                       frames_per_buffer=VoiceChatClient.CHUNK)

        # open read thread
        read_thread = threading.Thread(target=self.get_stream, daemon=True)
        read_thread.start()

    # create stream - records the player and sends the audio recording to the server
    def create_stream(self):
        while self.running:
            # read audio from this computer
            data = self.read_stream.read(VoiceChatClient.CHUNK)

            # send audio
            try:
                self.client_socket.sendto(data, (self.host, self.server_port))
            except OSError:
                continue

    # get stream - gets audio recording from the server and plays it
    def get_stream(self):
        while self.running:
            # get audio from server
            try:
                data, addr = self.client_socket.recvfrom(4096)
            except socket.timeout:
                continue
            except OSError:
                continue

            # get data index
            name, data = data.split(b'||')
            for user in self.write_streams.keys():
                if user.name == name.decode():
                    # change volume by multiplying each sample of the audio data by a volume factor
                    print(user.volume_factor)
                    data = numpy.frombuffer(data, dtype=numpy.int16) * user.volume_factor
                    data = data.astype(numpy.int16)

                    # play sound
                    self.write_streams[user].write(data.tobytes())
                    break
