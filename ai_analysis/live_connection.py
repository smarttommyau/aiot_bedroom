import socket # networking
import numpy as np # better array
import threading # multithreading
from time import sleep # delay
import zlib # for decompressing the data
class Live_connection:
    # format of new_frame_handler
    def __init__(self,host:str,port:int,new_frame_handler=None):
        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.died = False
        self.__msg = bytearray()
        self.height = 640
        self.width = 480 #change if camera resolution changes
        self.__thermal = np.array([],dtype='int32')
        self.__term = True
        self.new_frame_avaliable = False
        self.__decompress = True
        self.__frame_handler = new_frame_handler

        
    def printer(self,*values: object,nolog:bool):
        if not nolog:
            print(*values)

    def start_connection(self,nolog:bool = False):
        host = self.host
        port = self.port
        ss   = self.ss

        print("binding to",host,port)
        ss.bind((host,port))

        ss.listen(10)

        csocket = socket.socket()
        addrlist = []
        count = 0
        prompt = "n"
        while self.__term and count <2:
            while prompt != "y":
                csocket,addr = ss.accept()
                print("%s connected"% str(addr))
                if(addrlist.count(addr[0]) == 0):
                    print("accept?(y/n)")
                    prompt = input()
                else:
                    prompt= "y"
                if(prompt != "y" and prompt != ""):
                    csocket.send("rejected\n".encode('ascii'))
                else:
                    addrlist.append(addr[0])
                    csocket.send("accepted\n".encode('ascii'))
                    t1 = threading.Thread(target = self.start_recieve,args=(csocket,nolog))
                    t1.start()
            count+=1 
            prompt = "n"

# use multiprocess thing to call start_recieve
    def start_recieve(self,csocket,nolog:bool = False):
        printer = self.printer
        printer("recieving",nolog=nolog)
        # csocket is now the active recieving
        headerPending = True
        expectedData = 8
        size_thermal = 0
        size_visual = 0
        bufferedData = bytearray()
        thermalPending = True
        csocket.settimeout(10)

        while self.__term:
            if headerPending:
                bufferedData = bytearray()
                expectedData = 8
            #Receiving from client
            try:
                data = csocket.recv(expectedData)
            except:
                print('Error receiving data and exit')
                break
            if not data: 
                csocket.close()
                printer("Error to exit",nolog=nolog)
                break
            if headerPending:
                printer("new",nolog=nolog)
                size_thermal = (data[0] << 24) + (data[1] << 16) + (data[2] << 8) + data[3]
                size_visual = (data[4] << 24) + (data[5] << 16) + (data[6] << 8) + data[7]
                #print('size of frame: '+str(size))
                printer(str(size_thermal)+ "," + str(size_visual),nolog=nolog)
                expectedData = size_thermal
                headerPending = False
            else:
                expectedData = expectedData - len(data)
                bufferedData += data
                if thermalPending and expectedData <= 0:
                    expectedData = size_visual
                    thermalPending = False
                    t1 = threading.Thread(target=self.__thermal_data_process,args=(bufferedData.copy(),nolog))
                    t1.start()
                    bufferedData = bytearray()

                if expectedData <= 0:
                    self.__msg = bufferedData.copy()
                    thermalPending = True
                    bufferedData = bytearray()
                    headerPending = True
                    expectedData = 8
                    t1.join()
                    if self.__decompress:
                        self.new_frame_avaliable = True
                        printer("true",nolog=nolog)
                        if self.__frame_handler is not None:
                            threading.Thread(target=self.__frame_handler()).start()
                    else:
                        printer("continue",nolog=nolog)

    def __thermal_data_process(self,tempdata,nolog):
        self.__decompress = True
        printer = self.printer
        # print("bef:",len(tempdata))
        try:
            tempdata = zlib.decompress(tempdata)
        except:
            self.__decompress = False
            printer("fail to decompress",nolog=nolog)
        if not self.__decompress:
            return None
        # print("aft:",len(tempdata))
        temp = np.zeros([self.height,self.width],dtype='int32')
        for j in range(self.height):
            for i in range(self.width):
                # temp[j][i]+=tempdata[(j*self.width+i)*4]<<24
                # temp[j][i]+=tempdata[(j*self.width+i)*4+1]<<16
                temp[j][i]+=tempdata[(j*self.width+i)*2]<<8
                temp[j][i]+=tempdata[(j*self.width+i)*2+1]
        printer("decompressed",nolog=nolog)
        self.__thermal = temp
        return None



    def getcurrentframe(self):
        self.new_frame_avaliable = False
        return (self.__msg,self.__thermal)

    def terminate(self):
        self.__term = False
        self.died = True



