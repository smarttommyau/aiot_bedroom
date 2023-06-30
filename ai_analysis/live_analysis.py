# Version tends to fix performance issue by using native python instead of ipy
from live_connection import Live_connection 
from live_tkwindow import tkwindow, tkdialog
from live_detections import detection
from IoT.IoT import Fan_Control,Light_Control,Buzzer_Control
from audioplayer import AudioPlayer
import threading
from ultralytics import YOLO
from PIL import Image
from io import BytesIO, StringIO
import math
import time
import numpy as np
from loguru import logger
from collections import deque
from PIL import Image, ImageTk
import tkinter
from sys import argv

# Set whether print log
## Rubbish match to set nolog
nolog = True if len(argv)>=2 and argv[1] == 'nolog=true' else False



#Setup Logger
LogStream = StringIO()
logger.add("logs/file_{time}.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="50MB")
logger.add(LogStream)
logdeque = deque(maxlen=10)
posLogStream = 0

# Start up window
logger.info("Start main")
tkwindow = tkwindow()

# Load and Setup model
## you can change to other yolo model(they are not tested,but less cpu usage)
## TODO: Update to v8
model = YOLO("yolov8n.pt") # default yolov5x6

# Start up Network
## Setup Hardware
dialog = tkdialog("Prompt for IoT server",("Address",),("http://192.168.43.151:7777/controller",))
(IoT_addr,) = dialog.input

## Controllers
fan = Fan_Control(IoT_addr)
light = Light_Control(IoT_addr)
buzzer = Buzzer_Control(IoT_addr)
class aircon:
    def __init__(self,fan) -> None:
        self.status = False
        self.temperature = 25
        self.lastchange = 0
        self.fan = fan

    def temp_change(self,increment):
        timenow = time.time()
        if timenow - self.lastchange >300: #i.e. 5min
            aircon += increment
            self.lastchange = timenow
    def power(self,onOff):
        if self.status != onOff:
            self.status = onOff
            fan.set_fan_state(onOff)
            logger.info("Aircon "+("On" if onOff else "Off"))

aircon = aircon()

dialog = tkdialog("Prompt for setting up server for thermal camera",("IP(local)","Port"),("192.168.210","7777"))
(addr,port) = dialog.input
## Setup detection
detection = detection()
action = action(aircon,light,detection)

## Setup live connection to thermal camera
def new_frame_handler():
    (frame,thermal) = live_connection.getcurrentframe()
    image = Image.open(BytesIO(frame))
    results = model.prediction(image,classes=[0,59,63,67])
    # person, bed, laptop(as some phone can be detact by laptop), cell phone 
    tkwindow.updateImage(image=Image.fromarray(results[0].plot(pil=True))
    detection.update(results[0],thermal,time.time())
    

live_connection = Live_connection(addr,port,new_frame_handler)
connection_thread = threading.Thread(target=live_connection.start_connection,args=(nolog,))

def main_threadf():
    pass





## start internet incomming
tkwindow.start()
connection_thread.start()
main_thread = threading.Thread(target=main_threadf)
main_thread.start()

