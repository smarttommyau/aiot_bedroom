# Version tends to fix performance issue by using native python instead of ipy
from live_connection import Live_connection 
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

#Setup Logger
LogStream = StringIO()
logger.add("logs/file_{time}.log", format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", rotation="50MB")
logger.add(LogStream)
logdeque = deque(maxlen=10)
posLogStream = 0

# Load and Setup model
## you can change to other yolo model(they are not tested,but less cpu usage)
model = torch.hub.load('ultralytics/yolov5', 'yolov5x6', pretrained=True) # default yolov5x6
model.classes = [0,59,63,67]# person, bed, laptop(as some phone can be detact by laptop), cell phone 
torch.set_num_interop_threads(8)# improve performance, you may change according to your cpu
torch.set_num_threads(8)
#model.cpu() , if you want to use cpu;model.cuda() if you want to use gpu

logger.info("Start main")






