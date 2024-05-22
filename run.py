import threading
import queue
import time
import socket
import struct
import cv2

from ultralytics import YOLO

model = YOLO("best (13).pt")

lookup_dict = {
    0: 'Flame1',
    1: 'Flame2',
    2: 'Flame3',
    3: 'Flame4',
    4: 'Flame5',
    5: 'MQ7'
}

lookup_bytes = {
    'hue': b'HUE',
    'intensity': b'LED',
    'buzzer': b'BUZ'
}

class TCPWriterThread(threading.Thread):
    def __init__(self, ip, port, semaphore, command_queue):
        super().__init__()
        self.ip = ip
        self.port = int(port)
        self.semaphore = semaphore
        self.command_queue = command_queue
        self.connected = False
        self.socket = None

    def run(self):
        while True:
            if not self.connected:
                self.connect_to_server()
            self.semaphore.release()

            while self.connected:
                # Read sensor data and trigger LED control
                self.read_sensor_data()

                if not self.command_queue.empty():
                    # Clear the command queue before putting new intensity command
                    self.command_queue.queue.clear()
                    command = self.command_queue.get()
                    self.send_packet(command)
                time.sleep(0.1)

    def connect_to_server(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.ip, self.port))
            self.connected = True
            
            self.send_packet(('hue', 150))
            print("Connected to server.")
        except socket.error as e:
            print(f"Connection failed: {e}")
            time.sleep(1)

    def send_packet(self, command):
        try:
            header = lookup_bytes[command[0]]
            packet = struct.pack('3sB3x', header, command[1])
            self.socket.sendall(packet)
            print("Sent packet:", command)
            self.semaphore.release()
        except Exception as e:
            print(f"Error sending packet: {e}")
            self.connected = False
            
    def read_sensor_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.ip, self.port))
            print(f"Connected to {self.ip}:{self.port}")

            data = s.recv(24)

            if not data:
                print("Connection closed by server.")
                return

            floats = struct.unpack('6f', data)

            index = 0
            fire_detected = False
            for f in floats:
                print(f"{lookup_dict[index]} : {f}")
                
                if f > 1000.0:
                    fire_detected = True
                    break
                index += 1
                
            if fire_detected:
                print("Fire detected by sensor.")
                self.control_led(255)  # Light up the LEDs when fire is detected
                self.send_packet(('buzzer', True))  # Turn on the buzzer
            else:
                print("No fire detected by sensor.")
                self.control_led(0)  # Turn off the LEDs when no fire is detected
                self.send_packet(('buzzer', False))  # Turn off the buzzer

    def control_led(self, intensity):
        try:
            header = lookup_bytes['intensity']
            packet = struct.pack('3sB3x', header, intensity)
            self.socket.sendall(packet)
            print("LED Intensity Command Sent:", intensity)
            self.semaphore.release()
        except Exception as e:
            print(f"Error sending LED intensity command: {e}")
            self.connected = False

def detect_objects(current_frame, writer_thread):
    results = model.track(
        source=current_frame,
        conf=0.5,
        iou=0.5,
        imgsz=640,
        show=True,
        stream=True,
        persist=True,
    )

    fire_detected = False
    conf = 0
    message = "Fire detected"

    for result in results:
        if result.boxes is not None and result.boxes.conf is not None:
            conf_tensor = result.boxes.conf
            if conf_tensor.numel() == 1:
                conf = float(conf_tensor.item())
                fire_detected = True
                break

    if fire_detected:
        payload = {
            "confidence": conf,
            "message": message,
        }
        writer_thread.control_led(255)
        writer_thread.send_packet(('buzzer', 1))  # Turn on the buzzer
        print(f"Fire detected: {payload}")
    else:
        writer_thread.control_led(0)
        writer_thread.send_packet(('buzzer', 0))  # Turn off the buzzer
        print("No fire detected")

def main():
    ip = "192.168.4.1"
    port = 3030
    
    semaphore = threading.Semaphore(0)
    command_queue = queue.Queue()
    
    writer_thread = TCPWriterThread(ip, port, semaphore, command_queue)
    writer_thread.start()

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        detect_objects(frame, writer_thread)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
