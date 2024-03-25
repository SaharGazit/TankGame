import socket


def main():
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Server host and port
    server_host = "192.168.5.87"
    server_port = 12345

    # Connect to the server
    client_socket.connect((server_host, server_port))

    # Send a message to the server
    message = "Hello, server!"
    client_socket.send(message.encode())

    # Receive response from the server
    response = client_socket.recv(1024).decode()
    print("Response from server:", response)

    # Close the connection
    client_socket.close()

if __name__ == "__main__":
    main()