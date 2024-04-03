import socket
import threading

server_ip = '127.0.0.1'
server_port = 31410

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((server_ip, server_port))
server_socket.sendall("Sahar".encode())

running = True


def listen():
    while running:
        data = server_socket.recv(1024)
        # handle data


listening_thread = threading.Thread(target=listen, daemon=True)
listening_thread.start()
while running:
    message = input()
    if message == 'exit':
        running = False
    else:
        server_socket.send(message.encode())

server_socket.close()


