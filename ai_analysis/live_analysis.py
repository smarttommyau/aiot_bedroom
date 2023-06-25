# Version tends to fix performance issue by using native python instead of ipy
from live_connection import Live_connection 
from live_tkwindow import tkwindow, tkdialog
from IoT.IoT import Fan_Control,Light_Control,Buzzer_Control
from audioplayer import AudioPlayer
import threading
import torch
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
model = torch.hub.load('ultralytics/yolov5', 'yolov5x6', pretrained=True) # default yolov5x6
model.classes = [0,59,63,67]# person, bed, laptop(as some phone can be detact by laptop), cell phone 
torch.set_num_interop_threads(8)# improve performance, you may change according to your cpu
torch.set_num_threads(8)
#model.cpu() , if you want to use cpu;model.cuda() if you want to use gpu

# Start up Network
## Setup Hardware
dialog = tkdialog("Prompt for IoT server",("Address",),("http://192.168.43.151:7777/controller",))
(IoT_addr,) = dialog.input

## Controllers
fan = Fan_Control(IoT_addr)
light = Light_Control(IoT_addr)
buzzer = Buzzer_Control(IoT_addr)

dialog = tkdialog("Prompt for setting up server for thermal camera",("IP(local)","Port"),("192.168.210","7777"))
(addr,port) = dialog.input

## Setup live connection to thermal camera
live_connection = Live_connection(addr,port)
connection_thread = threading.Thread(target=live_connection.start_connection,args=(nolog,))

## Detection thread


## Action thread

## start internet incomming
connection_thread.start()


