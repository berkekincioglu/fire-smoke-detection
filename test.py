from ultralytics import YOLO
from roboflow import Roboflow


""" rf = Roboflow(api_key="5siQ9oaZdvO5kk6mGXOJ")
project = rf.workspace("projectai-6neok").project("deteksiasapdanapi")
version = project.version(4)
dataset = version.download("yolov8")

 """
# Initialize the YOLO model with configuration from the dataset
model = YOLO('yolov8m.yaml')

# If you have pre-trained weights you want to start from, specify the path here

# Train the model with specified parameters
res = model.train(
    data="data.yaml",
    epochs=3
)
