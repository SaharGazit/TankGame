import socket
import pyaudio

# Client settings
HOST = '127.0.0.1'
PORT = 12345
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Create a UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Open microphone stream
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Client started. Press Ctrl+C to exit.")

try:
    while True:
        # Read microphone data
        data = stream.read(CHUNK)

        # Send microphone data to server
        client_socket.sendto(data, (HOST, PORT))
except KeyboardInterrupt:
    pass
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()
    client_socket.close()
