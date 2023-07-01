from PIL import Image, ImageTk
import tkinter
from io import BytesIO
from os import _exit 


class tkvariables:
    def __init__(self,name,tkvar,window,update) -> None:
        self.name = name
        self.tkvar = tkvar
        self.getter = update
        self.window = window
    def update(self):
        self.tkvar.set(self.getter())
        self.window.after(1000,self.update)
        ## update should call after method to update the value
class tkwindow:
    def __init__(self,logger) -> None:
        # TODO: design for status indicator
        # TODO: design IoT indicator  
        self.window = tkinter.Tk()
        self.window.geometry('{}x{}'.format(1000,800))
        self.window.title('Frame Viewer')
        self.window.protocol("WM_DELETE_WINDOW", self.__onQuit)
        self.__imageLabel = tkinter.Label(self.window,text="Waiting...");
        self.__imageLabel.pack()
        self.__imageLabel.place(x=0,y=0,width=480,height=640)
        self.__tkpi = None
        button = tkinter.Button(self.window,text="!!Force Kill!!",command=self.__onQuit)
        button.place(x=0,y=641,width=480,height=60)
        button.pack()
        self.window.after(100,self.__updateImageLabel)
        self.logger = logger
            



    def __updateImageLabel(self,direct=False):
        if self.__tkpi is not None:
            self.__imageLabel.config(image=self.__tkpi)
        if direct != True:
            self.window.after(500,self.__updateImageLabel)

    def __onQuit(self):
        self.__imageLabel.destroy()
        self.window.destroy()
        ## Be carefuk of this _exit as it kill everthing in a bad way
        _exit(0)

    def start(self):
        self.logger.info("Start GUI")
        self.window.mainloop()

    def updateImage(self,frame=None,image=None):
        img = None
        if frame is None and image is None:
            return
        elif frame is None:
            img = image
        else:
            memoryFile = BytesIO(frame)
            img = Image.open(memoryFile)
        try:
            self.__tkpi = ImageTk.PhotoImage(img)
            self.__imageLabel.config(image=self.__tkpi)
            self.logger.info("Update Image")
        except:
            pass
        self.window.after_idle(self.__updateImageLabel, True);

class tkdialog:
    def __init__(self,title:str,label:tuple,default:tuple):
        self.input = list()
        self.__window = tkinter.Tk()
        self.__window.geometry('{}x{}'.format(300,150))
        self.__window.title(title)
        self.__entry = list()
        # create an entry widget for user input
        for txt,detxt in zip(label,default):
            tkinter.Label(self.__window,text=txt).pack()
            self.__entry.append(tkinter.Entry(self.__window))
            self.__entry[-1].insert(0,detxt)
            self.__entry[-1].pack()
        # create a button to submit the input
        self.__button = tkinter.Button(self.__window, text="Submit", command=self.__submit)
        self.__window.bind_all('<Return>',self.__submit)
        self.__button.pack()
    def start(self):
        self.__window.mainloop()

    def __submit(self,event=None):
        # event use to catch <return> event
        # get the input from the entry widget 
        for x in self.__entry:
            self.input.append(x.get())
        self.__window.destroy()
