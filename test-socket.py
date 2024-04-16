import socket
import struct


def main():
    host = "127.0.0.1"  # Localhost
    port = 3030

    # Start a TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        # Accept a connection
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")

            # Receive data from the client
            data = conn.recv(24)
            print(f"Received data from client: {data}")


if __name__ == "__main__":
    main()
