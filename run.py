from ultralytics import YOLO
import cv2
from flask import Flask, render_template
from flask_socketio import SocketIO, send
import socket
import json
import numpy as np


model = YOLO("best (13).pt")

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app, cors_allowed_origins="*")

def send_fire_detection(payload):
    # Convert payload to JSON string
    payload_json = json.dumps(payload)

    # Convert JSON string to bytes
    payload_bytes = payload_json.encode("utf-8")

    # Send data to the ESP32 via socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = "127.0.0.1"  # Replace with the ESP32 IP address
        port = 3030
        s.connect((host, port))
        s.sendall(payload_bytes)


def detect_objects(current_frame, current_tracked_ids):
    results = model.track(
        source=current_frame,
        conf=0.6,
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

        # Send payload to test-socket.py
        send_fire_detection(payload)

    return current_frame, current_tracked_ids


# SocketIO event handler for sending messages
@socketio.on("message")
def handle_message(message):
    print("received message: " + message)


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    tracked_ids = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame, tracked_ids = detect_objects(frame, tracked_ids)

        # print(f"Fire detected: {tracked_ids}")

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    socketio.run(app)



0.7 | 170

(50-100) (100-255)

a = (0, 255)
b = (0, 255)
c = (0, 255)
d = (0, 255)
e = (0, 255)
f = (0, 255)