from ultralytics import YOLO
import cv2

model = YOLO('best (3).pt')

def detect_objects(current_frame, current_tracked_ids):
    results = model.track(source=current_frame,
                          conf=0.5,  # Adjusted confidence
                          iou=0.5,   # Adjusted IoU
                          imgsz=640, 
                          show=True,
                          stream=True,
                          persist=True)

    new_ids = []
    for result in results:
        if result.boxes is None or result.boxes.id is None:
            continue

        boxes = result.boxes.data

        ids = result.boxes.id.cpu().numpy().astype(int)
        cls = result.boxes.cls.cpu().numpy().astype(int)

        for box, obj_id, cls in zip(boxes, ids, cls):
            if obj_id not in current_tracked_ids:
                new_ids.append(obj_id)

    current_tracked_ids.update(new_ids)

    return current_frame, current_tracked_ids


cap = cv2.VideoCapture(0)

tracked_ids = set()
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame, tracked_ids = detect_objects(frame, tracked_ids)

    print(f'Fire detected: {tracked_ids}')

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
