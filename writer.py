import threading
import queue
import time
import socket
import struct


lookup_bytes = {
    'hue' : b'HUE',
    'intensity' : b'LED',
    'buzzer' : b'BUZ'
}

lookup_bool = {
    'true' : True,
    'false' : False,
}

def is_socket_connected(sock):
    try:
        # Check the socket's error status
        error_code = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if error_code == 0:
            return True
        else:
            return False
    except socket.error:
        return False

class TCPWriterThread(threading.Thread):
    def __init__(self, ip, port, semaphore, command_queue):
        super().__init__()
        self.ip = ip
        self.port = int(port)
        self.semaphore = semaphore
        self.command_queue = command_queue
        self.connected = False
        self.socket = None  # Initialize socket here, don't create it until run()

    def run(self):
        while True:
            if not self.connected:
                self.connect_to_server()
            self.semaphore.release()  # Signal main thread

            # Wait for commands and send packets
            while self.connected:
                if not self.command_queue.empty():
                    command = self.command_queue.get()
                    self.send_packet(command)
                time.sleep(0.1)  # Sleep to avoid CPU hogging

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True
            print("Connected to server.")
        except socket.error as e:
            print(f"Connection failed: {e}")
            time.sleep(1)  # Wait before attempting to reconnect

    def send_packet(self, command):
        try:
            header = lookup_bytes[command[0]]
            packet = struct.pack('3sB3x', header, command[1])
            self.socket.sendall(packet)
            print("Sent packet:", command)
            self.semaphore.release()  # Signal main thread
        except Exception as e:
            print(f"Error sending packet: {e}")
            self.connected = False  # Disconnect on error



def main():
    ip = "192.168.4.1"
    port = 3030
    
    semaphore = threading.Semaphore(0)  # Binary semaphore
    command_queue = queue.Queue()
    
    writer_thread = TCPWriterThread(ip, port, semaphore, command_queue)
    writer_thread.start()
    
    while True:
        # Wait for connection
        semaphore.acquire()
        print("Ready.")
        
        # User input loop
        while True:
            message = input("What message do you wish to send? Available: [hue, intensity, buzzer]: ").strip().lower()
            
            if message == 'hue' or message == 'intensity':
                value = int(input(f"Enter {message} value (0-255): "))
                if value < 0 or value > 255:
                    print("Invalid value. Please enter a number between 0 and 255.")
                    continue
            elif message == 'buzzer':
                user_input = input("Enter buzzer value (true/false): ").strip().lower()
                if user_input != 'true' and user_input != 'false':
                    print("Invalid value. Please enter 'true' or 'false'.")
                    continue
                value = lookup_bool[user_input]
            else:
                print("Invalid command. Please enter 'hue', 'intensity', or 'buzzer'.")
                continue
            
            command_queue.put((message, value))
            break

if __name__ == "__main__":
    main()
