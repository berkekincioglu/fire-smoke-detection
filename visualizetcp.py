import socket
import struct

def main():
    host = "192.168.1.92"
    port = 3030
    lookup_dict = {
        0 : 'Flame1',
        1 : 'Flame2',
        2 : 'Flame3',
        3 : 'Flame4',
        4 : 'Flame5',
        5 : 'MQ7'
    }
    # Connect to the TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        print(f"Connected to {host}:{port}")

        while True:
            # Receive 24 bytes of data
            data = s.recv(24)

            if not data:
                print("Connection closed by server.")
                break

            # Parse the received data as floats
            floats = struct.unpack('6f', data)

            # Print the parsed floats
            index = 0
            print("Received floats from server:")
            for f in floats:
                print(f"{lookup_dict[index]} : {f}")
                index += 1
if __name__ == "__main__":
    main()
