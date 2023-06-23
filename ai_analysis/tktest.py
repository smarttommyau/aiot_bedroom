from live_connection import *
import threading
import time
from PIL import Image, ImageTk
import tkinter
import sys
from io import BytesIO

ip = input("The address to bind:")
connection = Live_connection(ip,7777)

t1 = threading.Thread(target = connection.start_connection)
t1.start()
start = time.time()
print("100")

def updateImageLabel(direct=False):
	imageLabel.config()
	if direct != True:
		window.after(100,updateImageLabel)

def onQuit():
	print('Quitting...')
	imageLabel.destroy()
	window.destroy()
def mainLoop():
    while True:
        while not connection.new_frame_avaliable:
            pass
        print("Hi")
        (frame,thermal) = connection.getcurrentframe()
        memoryFile = BytesIO(frame)
        img = Image.open(memoryFile)
        try:
            tkpi = ImageTk.PhotoImage(img)
            imageLabel.config(image=tkpi);
        except:
            pass
        window.after_idle(updateImageLabel, True);
	


window = tkinter.Tk()
window.geometry('{}x{}'.format(480,640))
window.title('Frame Viewer')
window.protocol("WM_DELETE_WINDOW", onQuit)
imageLabel = tkinter.Label(window,text="Waiting...");
imageLabel.pack()
imageLabel.place(x=0,y=0,width=480,height=640)
t2 = threading.Thread(target=mainLoop)
t2.start()
window.after(100,updateImageLabel)
window.mainloop()
connection.terminate()
sys.exit(0)
