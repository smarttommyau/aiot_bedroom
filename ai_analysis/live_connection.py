import socket

from PIL.Image import merge
import numpy as np
class Live_connection:
    def __init__(self,host:str,port:int):
        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.__msg = bytearray()
        self.__height = int()
        self.__width = int()
        self.__thermal = np.array(dtype='int32')
        self.__term = True
        self.csocket = socket.socket()
        self.new_frame_avaliable = False
        self.insync = False

    def start_connection(self):
        host = self.host
        port = self.port
        ss   = self.ss

        print("binding to",host,port)
        ss.bind((host,port))

        ss.listen(1)

        prompt = "n"
        csocket = socket.socket()

        while prompt != "y":
            csocket,addr = ss.accept()

            print("%s connected"% str(addr))
            print("accept?(y/n)")
            prompt = input()
            if(prompt != "y"):
                csocket.send("rejected\n".encode('ascii'))
                csocket.close()
        self.csocket = csocket
        csocket.send("accepted\n".encode('ascii'))

# use multiprocess thing to call start_recieve
    def start_recieve(self):
        csocket = self.csocket
        # csocket is now the active recieving
        while self.__term:
            message = ""
            while (message != "new" and message != "new thermal") and self.__term:
                try:
                    data = csocket.recv(1024)
                    if data:
                        message = str(data.decode('ascii'))
                    break;
                except UnicodeDecodeError:
                    print("invalid input recieved")

                print(message)

            if message == "new":
                self.__visual_data(csocket)
            else:
                self.__thermal_data(csocket)

            csocket.send("ok\n".encode('ascii'))

    def __thermal_data(self,csocket):
        info = csocket.recv(1024).decode('ascii').split()
        bufsize = int(info[0])
        self.width = int(info[1])
        self.height = int(info[2])
        print("1")
        csocket.send((str(bufsize) + " bytes is going to be recieve\n").encode('ascii'))
        print("2")
        temp = bytearray()
        while len(temp)<bufsize:
            data = csocket.recv(bufsize)
            temp += bytearray(data)
        templ = np.frombuffer(temp,dtype=np.int32)
        self.__thermal = templ
        print("3")
        csocket.send("recieved\n".encode('ascii'))
        print("recieved")
        self.insync = True


    def __visual_data(self,csocket):
        bufsize = int(csocket.recv(1024).decode('ascii'))
        print("1")
        csocket.send((str(bufsize) + " bytes is going to be recieve\n").encode('ascii'))
        print("2")
        temp = bytearray()
        while len(temp)<bufsize:
            data = csocket.recv(bufsize)
            temp += bytearray(data)
        self.__msg = temp
        print("3")
        csocket.send("recieved\n".encode('ascii'))
        print("recieved")
        self.new_frame_avaliable = True
        self.insync = False

    def getcurrentframe(self):
        self.new_frame_avaliable = False
        self.thermal_update = False
        return (self.__msg,self.__thermal)

    def terminate(self):
        self.__term = False
        self.csocket.close()
        self.ss.close()
        



