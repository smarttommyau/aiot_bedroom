import socket

# now is a random value
class Live_connection:
    def __init__(self,host:str,port:int):
        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.__msg = bytes()
        self.__term = True
        self.csocket = socket.socket()
        self.new_frame_avaliable = False

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
            bufsize = int(csocket.recv(1024).decode('ascii'))
            print("1")
            csocket.send((str(bufsize) + " bytes is going to be recieve\n").encode('ascii'))
            print("2")
            self.__msg = csocket.recv(bufsize*8)
            print("3")
            csocket.send("recieved\n".encode('ascii'))
            self.new_frame_avaliable = True

    def getcurrentframe(self):
        self.new_frame_avaliable = False
        return self.__msg

    def terminate(self):
        self.__term = False
        self.csocket.close()
        self.ss.close()
        



