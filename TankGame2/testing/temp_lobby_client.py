import socket

server_ip = '127.0.0.1'
server_port = 31410

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect((server_ip, server_port))
server_socket.sendall("Sahar".encode())

while True:
    a = input()
    if a == "exit":
        break
    server_socket.sendall(a.encode())
