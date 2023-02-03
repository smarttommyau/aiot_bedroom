from live_connection import Live_connection
import threading
import torch
from PIL import Image
import io

model = torch.hub.load('ultralytics/yolov5', 'yolov5x6', pretrained=True)
model.classes = [0,59,63,67]
torch.set_num_interop_threads(8)
torch.set_num_threads(8)

live_connection = Live_connection(7777)

live_connection.start_connection()

t1 = threading.Thread(live_connection.start_recieve())
t1.start()

while True :
    #get data
    if live_connection.new_frame_avaliable:
        (frame,thermaldata)= live_connection.getcurrentframe()
        image = Image.open(io.BytesIO)
        
    #predict with model

    
