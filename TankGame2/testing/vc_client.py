# this is a test voice chat used between two people

# import AudioSender and AudioReceiver from the vidstream library.
# As the name suggests, one is used to send audio and one to receive audio
from vidstream import AudioSender
from vidstream import AudioReceiver

# threading is used in order for the sending and receiving function to run in parallel
import threading
import socket  # for a sole purpose of obtaining this client's ipv4 address

CLIENT_IP = "192.168.5.87"  # put the other client's ipv4 here

# create thread for receiving voice
receiver = AudioReceiver(socket.gethostbyname(socket.gethostname()), 9999)
receive_thread = threading.Thread(target=receiver.start_server)

# create thread for sending voice
sender = AudioSender(CLIENT_IP, 5555)
sender_thread = threading.Thread(target=sender.stop_stream)

# start threads
receive_thread.start()
sender_thread.start()

