import socket
import numpy as np
import threading
from time import sleep
class Live_connection:
    def __init__(self,host:str,port:int):
        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.__msg = bytearray()
        self.__newmsg = bytearray()
        self.height = int()
        self.width = int()
        self.__thermal = np.array([],dtype='int32')
        self.__newthermal = np.array([],dtype='int32')
        self.__term = True
        self.new_frame_avaliable = False
        self.__new_frameid = ""
        self.__synced = False # true thermal, flase visual

        

    def start_connection(self):
        host = self.host
        port = self.port
        ss   = self.ss

        print("binding to",host,port)
        ss.bind((host,port))

        ss.listen(2)

        prompt = "n"
        csocket = socket.socket()
        addrlist = []
        count =0
        while self.__term and count <2:
            while prompt != "y":
                csocket,addr = ss.accept()
                print("%s connected"% str(addr))
                if(addrlist.count(addr[0]) == 0):
                    print("accept?(y/n)")
                    prompt = input()
                else:
                    prompt= "y"
                if(prompt != "y"):
                    csocket.send("rejected\n".encode('ascii'))
                    csocket.close()
                else:
                    addrlist.append(addr[0])
            csocket.send("accepted\n".encode('ascii'))
            t1 = threading.Thread(target = self.start_recieve,args=(csocket,))
            t1.start()
            count+=1 
            prompt = "n"

# use multiprocess thing to call start_recieve
    def start_recieve(self,csocket):
        print("recieving")
        # csocket is now the active recieving
        state = ""
        while not(state=="true" or state=="false"):
            state = str(csocket.recv(2048).decode('ascii'))    
        csocket.send("setup fin\n".encode('ascii'))
        while self.__term:
            message = ""
            while not(message == "new") and self.__term:
                try:
                    message = str(csocket.recv(4096).decode('ascii'))
                    break;
                except UnicodeDecodeError:
                    print("invalid input recieved")

                print(message)

            csocket.send("ok\n".encode('ascii'))
            splited = message.split()
            if state == "true":
                self.__visual_data(csocket,splited[1])
            else:
                self.__thermal_data(csocket,splited[1])


    def __thermal_data(self,csocket,frameid):
        print("thermal",frameid)
        info = csocket.recv(1024).decode('ascii').split()
        bufsize = int(info[0])
        self.width = int(info[1])
        self.height = int(info[2])
        print("1")
        csocket.send((str(bufsize) + " bytes is going to be recieve\n").encode('ascii'))
        print("2")
        tempdata = bytearray()
        while len(tempdata)<bufsize:
            data = csocket.recv(bufsize)
            tempdata += bytearray(data)
        t1 = threading.Thread(target = self.__thermal_data_process,args=(csocket,frameid,tempdata))
        t1.start()
    def __thermal_data_process(self,csocket,frameid,tempdata):
        temp = np.zeros([self.height,self.width],dtype='int32')
        for j in range(self.height):
            for i in range(self.width):
                temp[j][i]+=tempdata[(j*self.width+i)*4]<<24
                temp[j][i]+=tempdata[(j*self.width+i)*4+1]<<16
                temp[j][i]+=tempdata[(j*self.width+i)*4+2]<<8
                temp[j][i]+=tempdata[(j*self.width+i)*4+3]
                
        self.__newthermal = temp
        print("3")
        csocket.send("recieved\n".encode('ascii'))
        print("recievedTh",frameid)
        retry = True
        count = 0
        while retry and count <2:
            if (frameid == self.__new_frameid):
                self.__synced = True 
                self.new_frame_avaliable = True
                self.__msg = self.__newmsg
                self.__thermal = self.__newthermal
                retry = False
            elif(frameid!=self.__new_frameid and not self.__synced):
                self.__new_frameid = frameid
                self.__synced = True
                retry = False
            else:
                sleep(0.3)
                retry = True
                count +=1


    def __visual_data(self,csocket,frameid):
        print("visual",frameid)
        bufsize = int(csocket.recv(1024).decode('ascii'))
        print("1")
        csocket.send((str(bufsize) + " bytes is going to be recieve\n").encode('ascii'))
        print("2")
        temp = bytearray()
        while len(temp)<bufsize:
            data = csocket.recv(bufsize)
            temp += bytearray(data)
        self.__newmsg = temp
        print("3")
        csocket.send("recieved\n".encode('ascii'))
        print("recievedVi",frameid)
        retry = True
        count  = 0
        while retry and count <2:
            if (frameid == self.__new_frameid):
                self.__synced = False
                self.new_frame_avaliable = True
                self.__msg = self.__newmsg
                self.__thermal = self.__newthermal
                retry = False
            elif(frameid!=self.__new_frameid and self.__synced):
                self.__new_frameid = frameid
                self.__synced = False
                retry = False
            else:
                sleep(0.3)
                retry = True
                count +=1
        

    def getcurrentframe(self):
        self.new_frame_avaliable = False
        return (self.__msg,self.__thermal)

    def terminate(self):
        self.__term = False
        self.csocket.close()
        self.ss.close()
        



