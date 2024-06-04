import socket
import pyaudio
import threading
import protocol
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

    # initiates the voice chat client
    # lobby id - the correct voice server port for this lobby is equal to protocol.vcserver_port plus the lobby id
    # so for example, if protocol.vcserver_port is 40000, and this lobby is number 10, the port would be 40010
    # port - this is the port the client uses that the server can recognize from previous interactions
    def __init__(self, lobby_id, client_port, key):
        # server ip and port
        self.host = protocol.server_ip
        self.server_port = protocol.vcserver_port + lobby_id

        # initialize PyAudio
        self.audio = pyaudio.PyAudio()

        # create a UDP socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('0.0.0.0', client_port + 2))
        # timeout: the client stops listening if it doesn't get anything for a second
        self.client_socket.settimeout(1)

        self.running = False  # true as long as the client is running
        self.input_stream = None  # stream for recording audio from this user
        self.output_streams = {}  # dictionary that contains a different stream for every user, in order to play their audio

        self.aes_key = key

    # starts the client: plays audio from other users, and listens to this user's audio
    # users - a list of users, used to indentify which stream belongs to whom.
    def start(self, users):
        self.running = True
        # open input stream.
        # this is a "stream" of data that can contain audio data, and can play it constantly
        self.input_stream = self.audio.open(format=VoiceChatClient.FORMAT, channels=VoiceChatClient.CHANNELS,
                                            rate=VoiceChatClient.RATE, input=True,
                                            frames_per_buffer=VoiceChatClient.CHUNK)

        # open input thread
        input_thread = threading.Thread(target=self.record_audio, daemon=True)
        input_thread.start()

        # reset streams
        self.output_streams = {}
        # create an output stream for each user
        for user in users:
            self.output_streams[user] = self.audio.open(format=VoiceChatClient.FORMAT,
                                                        channels=VoiceChatClient.CHANNELS,
                                                        rate=VoiceChatClient.RATE, output=True,
                                                        frames_per_buffer=VoiceChatClient.CHUNK)

        # open read thread
        read_thread = threading.Thread(target=self.play_audio, daemon=True)
        read_thread.start()

    # records this user and sends the audio to the server
    def record_audio(self):
        while self.running:
            # read audio from this computer
            data = self.input_stream.read(VoiceChatClient.CHUNK)

            try:
                # send audio
                data = protocol.encrypt_data(self.aes_key, data)
                protocol.send_data(data, self.client_socket, (self.host, self.server_port))
            # prevent crashing if server crashed
            except OSError:
                print("VCCLIENT: server stopped responding")
                self.running = False

    # receives audio from the server, writes it in the correct stream, and plays it
    def play_audio(self):
        while self.running:
            # get audio from server
            try:
                data, addr = protocol.receive_data(self.client_socket, True)
                data = protocol.decrypt_data(self.aes_key, data)
            # timeout is triggered after the server doesn't send anything, to check if self.running is still true.
            # this is to prevent the program to get stuck waiting for data, while it actually supposed to stop.
            except socket.timeout:
                continue
            # prevent crashing if server crashed
            except OSError:
                print("VCCLIENT: server stopped responding")
                self.running = False
                continue

            # audio consists of the username the voice belongs to, and the audio, separated by ||.
            name, data = data.split(b'||')
            # find user
            for user in self.output_streams.keys():
                if user.name == name.decode():
                    # change volume by multiplying each sample of the audio data by a user's volume factor, using numpy
                    data = numpy.frombuffer(data, dtype=numpy.int16) * user.volume_factor
                    data = data.astype(numpy.int16)

                    # play the sound after it was adjusted to the right volume.
                    self.output_streams[user].write(data.tobytes())
                    break
