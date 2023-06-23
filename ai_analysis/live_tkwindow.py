import threading
from PIL import Image, ImageTk
import tkinter
from io import BytesIO


class tkwindow:
    def __init__(self) -> None:
        self.__window = tkinter.Tk()
        self.__window.geometry('{}x{}'.format(480,640))
        self.__window.title('Frame Viewer')
        self.__window.protocol("WM_DELETE_WINDOW", self.__onQuit)
        self.__imageLabel = tkinter.Label(self.__window,text="Waiting...");
        self.__imageLabel.pack()
        self.__imageLabel.place(x=0,y=0,width=480,height=640)
        t1 = threading.Thread(target=self.__tkwindow)
        t1.start()
        return None


    def __updateImageLabel(self,direct=False):
        self.__imageLabel.config()
        if direct != True:
            self.__window.after(100,self.__updateImageLabel)

    def __onQuit(self):
        self.__imageLabel.destroy()
        self.__window.destroy()

    def __tkwindow(self):
        self.__window.after(100,self.__updateImageLabel)
        self.__window.mainloop()

    def updateImage(self,frame):
        memoryFile = BytesIO(frame)
        img = Image.open(memoryFile)
        try:
            tkpi = ImageTk.PhotoImage(img)
            self.__imageLabel.config(image=tkpi);
        except:
            pass
        self.__window.after_idle(self.__updateImageLabel, True);
