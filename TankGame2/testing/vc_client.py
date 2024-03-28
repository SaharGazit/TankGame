import random
import socket
import pyaudio

HOST = '127.0.0.1'  # server ip
PORT = random.randrange(10000, 50000)  # port

# determines the size of each block of audio data that is processed at a time
CHUNK = 1024
# states how many samples of audio are played or captured every second. has to match with the server's rate
RATE = 44100

# the audio data's format. should stay pyaudio.paInt16 (16-bit signed integer format) as it is a common format for audio data
FORMAT = pyaudio.paInt16
# 1 - mono audio (all audio comes from a single channel) 2 - stereo audio (comes from multiple channels, like left and right)
CHANNELS = 1

# initialize PyAudio
audio = pyaudio.PyAudio()

# create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('127.0.0.1', 40000))
server_address = None

# Open microphone stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

print("Client started. Press Ctrl+C to exit.")

try:
    while True:
        # read microphone data
        data = stream.read(CHUNK)

        # send microphone data to server
        client_socket.sendto(data, (HOST, PORT))

        data, addr = client_socket.recvfrom(4096)

        # Play received audio
        stream.write(data)
except KeyboardInterrupt:
    pass
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()
    client_socket.close()
