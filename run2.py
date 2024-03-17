import cv2
from ultralytics import YOLO


model = YOLO('best.pt')
results = model.track(source=0, imgsz=680, conf=0.4, show=True)