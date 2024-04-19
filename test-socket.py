import socket


def main():
    host = "127.0.0.1"
    port = 3030

    # Start a TCP server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()

        print(f"Server listening on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    decoded_data = data.decode("utf-8")
                    print(f"Received data from client : {decoded_data}")


if __name__ == "__main__":
    main()
