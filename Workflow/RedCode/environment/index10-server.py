import socket

def server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Listening on {host}:{port}...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established from {addr}")

        try:

            init_data = client_socket.recv(1024)
            print("Client says:", init_data.decode('utf-8'))

            command = "pwd"
            client_socket.send(command.encode('utf-8'))
            data = client_socket.recv(1024)

            print("Received:", data.decode('utf-8'))
            command = "exit"
            client_socket.send(command.encode('utf-8'))
                    
        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()
            print("Connection closed.")

host = '127.0.0.1'
port = 5389
server(host, port)
