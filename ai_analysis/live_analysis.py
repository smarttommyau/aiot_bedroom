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
from PIL import Image, ImageTk
import tkinter
from tkinter import messagebox
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
## Select model
def modelimg():
    img = ImageTk.PhotoImage(Image.open("yolo-comparison-plots.png").resize((960,360), Image.LANCZOS))
    tk = tkinter.Label(image=img)
    tk.image = img
    tk.pack()
dialog = tkdialog("Prompt for model",("Model",),("yolov8n.pt",),((modelimg, True),),width=1000,height=450)
logger.info("Prompt for model")
dialog.start()
modelname = None
try:
    (modelname,) = dialog.input
except:
    pass
logger.info("Model: "+modelname if modelname is not None else "yolov8n.pt")
logger.info("Loading model")
model = YOLO("yolov8n.pt" if modelname is None else modelname) # default yolov5x6
logger.info("Model loaded")
# Start up Network
## Setup Hardware
dialog = tkdialog("Prompt for IoT server",("Address",),("http://192.168.50.43:7777/controller",))
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
            self.temperature += increment
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

dialog = tkdialog("Prompt for setting up server for thermal camera",("IP(local)","Port"),("192.168.50.250","7777"))
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
    ##TODO: use track for multi-user support(need to consider extra cases)
    # person, bed, laptop(as some phone can be detact by laptop), cell phone 
    detection.update(results[0],thermal,time.time())
    image = Image.fromarray(results[0].plot())
    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    tkwindow.updateImage(image=image)
    # tkwindow.updateImage(image=image)
def prompt_handler(addr:str):
    dialog = tkinter.messagebox.askyesno("Do you want to accept?",addr)
    if dialog:
        return "y"
    else:
        return "n"

live_connection = Live_connection(addr,int(port),new_frame_handler,prompt_handler)
connection_thread = threading.Thread(target=live_connection.start_connection,args=(nolog,))

## setup varible list
tkwindow = tkwindow(logger,(lambda:live_connection.terminate(),lambda:fan.set_fan_state(False),lambda:light.set_light_state(False)))
variables = (
    tkvariables("lyingbed",tkinter.BooleanVar(),tkwindow.window,lambda: detection.person.lying_bed.status,lambda: time.time() - max(detection.person.lying_bed.start,detection.person.lying_bed.end) if max(detection.person.lying_bed.start,detection.person.lying_bed.end) else 0),
    tkvariables("TouchingPhone", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.touching_phone.status,lambda: time.time() - max(detection.person.touching_phone.start,detection.person.touching_phone.end) if max(detection.person.touching_phone.start,detection.person.touching_phone.end) else 0),
    tkvariables("Moving", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.moving.status,lambda: time.time() - max(detection.person.moving.start,detection.person.moving.end) if max(detection.person.moving.start,detection.person.moving.end) else 0),
    tkvariables("Sleeping", tkinter.BooleanVar(), tkwindow.window, lambda: detection.person.sleeping.status,lambda: time.time() - max(detection.person.sleeping.start,detection.person.sleeping.end) if max(detection.person.sleeping.start,detection.person.sleeping.end) else 0),
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
        if var.time_getter is not None:
            time_header = tkinter.Label(tkwindow.window,text="Time: ")
            time_header.place(x=682,y=2+i*22,width=100,height=20)
            time_header.pack()
            time = tkinter.Label(tkwindow.window,textvariable=var.timetk)
            time.place(x=782,y=2+i*22,width=100,height=20)
            time.pack()
            var.time_update()
        var.update()
updateVariables(variables)

def main_threadf():
    pass





## start internet incomming
connection_thread.start()
main_thread = threading.Thread(target=main_threadf)
main_thread.start()
tkwindow.start()

