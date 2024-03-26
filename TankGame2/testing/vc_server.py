import socket
import pyaudio

# Server settings
HOST = '127.0.0.1'
PORT = 12345
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
audio = pyaudio.PyAudio()

# create a UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))

print("Server listening...")

# Accept connection
client_address = None

# Open stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)

try:
    while True:
        data, addr = server_socket.recvfrom(4096)
        if client_address is None:
            client_address = addr
            print(f"Client connected from {client_address}")

        # Play received audio
        stream.write(data)
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()
    server_socket.close()