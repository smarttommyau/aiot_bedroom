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
from tkinter import font as TKfont
from tkinter import messagebox
from audioplayer import AudioPlayer
from sys import argv

# Set whether print log
## Rubbish match to set nolog
nolog = True if len(argv)>=2 and argv[1] == 'nolog=true' else False
fontsize = 15


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
## Select model
def modelimg():
    img = ImageTk.PhotoImage(Image.open("yolo-comparison-plots.png").resize((960,360), Image.LANCZOS))
    tk = tkinter.Label(image=img)
    tk.image = img
    tk.pack()
dialog = tkdialog("Prompt for model(Recommend to stay as what it is)",("Model",),("yolov8m.pt",),((modelimg, True),),width=1000,height=450)
# Using lighter model may cause high random KE making KE detection unusable
logger.info("Prompt for model")
dialog.start()
modelname = None
try:
    (modelname,) = dialog.input
except:
    pass
logger.info("Model: "+modelname if modelname is not None else "yolov8m.pt")
logger.info("Loading model")
model = YOLO("yolov8m.pt" if modelname is None else modelname) # default yolov5x6
logger.info("Model loaded")
# Start up Network
## Setup Hardware
dialog = tkdialog("Prompt for IoT server",("Address",),("http://192.168.137.160:7777/controller",))
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
class CaringService:
    def __init__(self):
        self.status = False
        self.__audio = AudioPlayer(".\\music\\Are_you_feeling_well.mp3")
        self.__audiohk = AudioPlayer(".\\music\\NotComfort(zh_hk).mp3")
        self.__audiocn = AudioPlayer(".\\music\\NotComfort(zh_cn).mp3")
    def power(self,onOff):
        if self.status != onOff:
            self.status = onOff
            logger.info("Caring Service "+("On" if onOff else "Off"))
            if onOff:
                threading.Thread(target=self.play).start()

    def play(self):
        self.__audio.play(block=True)
        self.__audiohk.play(block=True)
        self.__audiocn.play(block=True)
                
            


aircon_ = aircon(fan)
ambulance_ = ambulance(buzzer)
caring = CaringService()

dialog = tkdialog("Prompt for setting up server for thermal camera",("IP(local)","Port"),("192.168.137.1","7777"))
logger.info("Prompt for setting up server for thermal camera")
dialog.start()
(addr,port) = dialog.input
logger.info("Thermal camera address: "+addr+":"+port)
## Setup detection
detection = detection(logger)
action = action(
    aircon=aircon_,
    light=light,
    ambulance=ambulance_,
    caring=caring,
    detection=detection,
    logger=logger
    )

## Setup live connection to thermal camera
concurrent_limit = 4
concurent_counter = 0
def new_frame_handler():
    # global concurent_counter
    # concurent_counter += 1
    # if concurent_counter > concurrent_limit:
    #     return
    (frame,thermal) = live_connection.getcurrentframe()
    image = Image.open(BytesIO(frame))
    results = model.predict(image,classes=[0,59,63,67])
    ##future: use track for multi-user support(need to consider extra cases)
    ## need to be implement carefully or else logic maybe broken
    # person, bed, laptop(as some phone can be detact by laptop), cell phone 
    detection.update(results[0],thermal,time.time())
    image = Image.fromarray(results[0].plot())
    b, g, r = image.split()
    image = Image.merge("RGB", (r, g, b))
    tkwindow.updateImage(image=image)
    # concurent_counter -= 1
def prompt_handler(addr:str):
    dialog = tkinter.messagebox.askyesno("Do you want to accept?",addr)
    if dialog:
        return "y"
    else:
        return "n"
def socket_close_handler():
    logger.info("Connection closed")
    tkwindow.updateImage()
    detection.reset()

live_connection = Live_connection(addr,int(port),new_frame_handler,prompt_handler,socket_close_handler)
connection_thread = threading.Thread(target=live_connection.start_connection,args=(nolog,))

## setup varible list
tkwindow = tkwindow(logger,fontsize,(lambda:live_connection.terminate(),lambda:fan.set_fan_state(False),lambda:light.set_light_state(False)))
variables = (
    tkvariables("Person",tkinter.StringVar(),tkwindow.window,lambda: "True" if detection.person_presence.status else "False",lambda: round(time.time() - max(detection.person_presence.start,detection.person_presence.end),2) if max(detection.person_presence.start,detection.person_presence.end) else 0),
    tkvariables("lyingbed",tkinter.StringVar(),tkwindow.window,lambda: "True" if detection.person.lying_bed.status else "False" ,lambda: round(time.time() - max(detection.person.lying_bed.start,detection.person.lying_bed.end),2) if max(detection.person.lying_bed.start,detection.person.lying_bed.end) else 0),
    tkvariables("TouchPhone", tkinter.StringVar(), tkwindow.window, lambda: "True" if detection.person.touching_phone.status else "False",lambda: round(time.time() - max(detection.person.touching_phone.start,detection.person.touching_phone.end),2) if max(detection.person.touching_phone.start,detection.person.touching_phone.end) else 0),
    tkvariables("Moving", tkinter.StringVar(), tkwindow.window, lambda: "True" if detection.person.moving.status else "False",lambda: round(time.time() - max(detection.person.moving.start,detection.person.moving.end),2) if max(detection.person.moving.start,detection.person.moving.end) else 0),
    tkvariables("Sleeping", tkinter.StringVar(), tkwindow.window, lambda: "True" if detection.person.sleeping.status else "False",lambda: round(time.time() - max(detection.person.sleeping.start,detection.person.sleeping.end),2) if max(detection.person.sleeping.start,detection.person.sleeping.end) else 0),
    tkvariables("Temperature", tkinter.IntVar(), tkwindow.window, lambda: round(detection.person.temperature,2)),
    tkvariables("FlipOrBigMovement",tkinter.IntVar(),tkwindow.window,lambda: detection.person.EffectiveMoves.counter,extra_button=("Reset",lambda: detection.person.EffectiveMoves.reset())),
    tkvariables("BedTemperature", tkinter.IntVar(), tkwindow.window, lambda: round(detection.bed.temperature,2)),
    tkvariables("Ambulance", tkinter.StringVar(), tkwindow.window, lambda: "True" if action.ambulance.status else "False"),
    tkvariables("Aircon", tkinter.StringVar(), tkwindow.window, lambda: "True" if action.aircon.status else "False"),
    tkvariables("AirconTemp", tkinter.IntVar(), tkwindow.window, lambda: round(action.aircon.temperature,2)),
    tkvariables("Light", tkinter.StringVar(), tkwindow.window, lambda: "True" if action.light.get_light_state() else "False"),
)

def updateVariables(variables) -> None:
    length = len(variables) + 1
    height = 1/(length-1)
    for i,var in enumerate(variables):
        name = tkinter.Label(tkwindow.window,text=var.name,font=TKfont.Font(size=fontsize))
        name.place(relx=0.5,rely=i/length,relheight=height,relwidth=0.1)
        item = tkinter.Label(tkwindow.window,textvariable=var.tkvar,font=TKfont.Font(size=fontsize))
        item.place(relx=0.61,rely=i/length,relheight=height,relwidth=0.1)
        k = False
        if var.time_getter is not None:
            time_header = tkinter.Label(tkwindow.window,text="Time: ",font=TKfont.Font(size=fontsize))
            time_header.place(relx=0.72,rely=i/length,relheight=height,relwidth=0.1)
            time = tkinter.Label(tkwindow.window,textvariable=var.timetk,font=TKfont.Font(size=fontsize))
            time.place(relx=0.83,rely=i/length,relheight=height,relwidth=0.1)
            var.time_update()
            k = True
        if var.extra_button is not None:
            button = tkinter.Button(tkwindow.window,text=var.extra_button[0],command=var.extra_button[1],font=TKfont.Font(size=int(fontsize/1.1)))
            button.place(relx=0.94 if k else 0.8,rely=i/length,relheight=height,relwidth=0.05)
        var.update()
updateVariables(variables)

def main_threadf():
    pass





## start internet incomming
connection_thread.start()
main_thread = threading.Thread(target=main_threadf)
main_thread.start()
tkwindow.start()

