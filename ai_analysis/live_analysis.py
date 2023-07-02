# Version tends to fix performance issue by using native python instead of ipy
from live_connection import Live_connection 
from live_tkwindow import tkwindow, tkdialog,tkvariables
from live_detections import detection
from live_action import action
from IoT.IoT import Fan_Control,Light_Control,Buzzer_Control
import threading
from ultralytics import YOLO
from io import BytesIO, StringIO
import time
from loguru import logger
from collections import deque
from PIL import Image
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

# Load and Setup model
## you can change to other yolo model(they are not tested,but less cpu usage)
## TODO: Update to v8
logger.info("Loading model")
model = YOLO("yolov8n.pt") # default yolov5x6
logger.info("Model loaded")
# Start up Network
## Setup Hardware
dialog = tkdialog("Prompt for IoT server",("Address",),("http://192.168.0.240:7777/controller",))
logger.info("Prompt for IoT server")
dialog.start()
(IoT_addr,) = dialog.input
logger.info("IoT server address: "+IoT_addr)
## Controllers
logger.info("Test Fan Controller")
fan = Fan_Control(IoT_addr)
fan.set_fan_state(True)
time.sleep(2)
fan.set_fan_state(False)
time.sleep(1)
logger.info("Test Light Controller")
light = Light_Control(IoT_addr)
light.set_light_state(True)
time.sleep(2)
light.set_light_state(False)
time.sleep(1)
logger.info("Test Buzzer Controller")
buzzer = Buzzer_Control(IoT_addr)
buzzer.send_buzzer_command(1000,2)
time.sleep(2)
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
class ambulance:
    def __init__(self,buzzer) -> None:
        self.status = False
        self.buzzer = buzzer
        self.tolerance = 3
        self.tolerance_counter = 3
        self.lock = threading.Event()
        self.thread = threading.Thread(target=self.__play_ambulace)
        self.thread.start()

    def power(self,onOff):

        if onOff:
            self.tolerance_counter -=1
            if self.tolerance_counter <=0:
                self.status = True
                logger.info("Ambulance Called")
                self.lock.set()
        else:
            self.tolerance_counter = self.tolerance
            if self.status: 
                self.status = False           
                logger.info("Ambulance Cancelled")
                self.lock.clear()
    def __play_ambulace(self):
        flutuator = False
        while True:
            self.lock.wait()
            if flutuator:
                flutuator = False
            else:
                flutuator = True
            self.buzzer.send_buzzer_command(1480 if flutuator else 1407, 1000)
            time.sleep(1)


aircon_ = aircon(fan)
ambulance_ = ambulance(buzzer)

dialog = tkdialog("Prompt for setting up server for thermal camera",("IP(local)","Port"),("192.168.0.210","7777"))
logger.info("Prompt for setting up server for thermal camera")
dialog.start()
(addr,port) = dialog.input
logger.info("Thermal camera address: "+addr+":"+port)
## Setup detection
detection = detection(logger)
action = action(aircon_,light,ambulance_,detection,logger)

## Setup live connection to thermal camera
def new_frame_handler():
    (frame,thermal) = live_connection.getcurrentframe()
    image = Image.open(BytesIO(frame))
    results = model.predict(image,classes=[0,59,63,67])
    # person, bed, laptop(as some phone can be detact by laptop), cell phone 
    detection.update(results[0],thermal,time.time())
    image = Image.fromarray(results[0].plot())
    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    tkwindow.updateImage(image=image)
    # tkwindow.updateImage(image=image)
    

live_connection = Live_connection(addr,int(port),new_frame_handler)
connection_thread = threading.Thread(target=live_connection.start_connection,args=(nolog,))

## setup varible list
tkwindow = tkwindow(logger)
variables = (
    tkvariables("lyingbed",tkinter.BooleanVar(),tkwindow.window,lambda: detection.person.lying_bed.status),
    tkvariables("TouchingPhone", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.touching_phone.status),
    tkvariables("Moving", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.moving.status),
    tkvariables("Sleeping", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.sleeping.status),
    tkvariables("Temperature", tkinter.IntVar(), tkwindow.window, lambda: detection.person.temperature),
    tkvariables("BedTemperature", tkinter.IntVar(), tkwindow.window, lambda: detection.bed.temperature),
    tkvariables("Ambulance", tkinter.BooleanVar(), tkwindow.window, lambda: action.ambulance.status),
    tkvariables("Aircon", tkinter.BooleanVar(), tkwindow.window, lambda: action.aircon.status),
    tkvariables("AirconTemp", tkinter.IntVar(), tkwindow.window, lambda: action.aircon.temperature),
    tkvariables("Light", tkinter.BooleanVar(), tkwindow.window, lambda: action.light.get_light_state()),
)

def updateVariables(variables) -> None:
    for i,var in enumerate(variables):
        name = tkinter.Label(tkwindow.window,text=var.name)
        name.place(x=482,y=2+i*22,width=100,height=20)
        name.pack()
        item = tkinter.Label(tkwindow.window,textvariable=var.tkvar)
        item.place(x=582,y=2+i*22,width=100,height=20)
        item.pack()
        var.update()
updateVariables(variables)

def main_threadf():
    pass





## start internet incomming
connection_thread.start()
main_thread = threading.Thread(target=main_threadf)
main_thread.start()
tkwindow.start()

