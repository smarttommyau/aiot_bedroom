import socket

# now is a random value
THERMAL_FRAME_SIZE = 1024 * 1024 * 32
class Live_connection:
    def __init__(self,port):
        self.ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        self.host = socket.gethostname()
        self.port = port
        self.msg = ""
        self.term = True
        self.csocket = socket.socket()

    def start_connection(self):
        host = self.host
        port = self.port
        ss   = self.ss

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
                csocket.send("rejected".encode('anscii'))
                csocket.close()
        self.csocket = csocket
    def start_recieve(self):
        csocket = self.csocket
        # csocket is now the active recieving
        while self.term:
            csocket.send("accepted".encode('anscii'))
            self.msg = csocket.recv(THERMAL_FRAME_SIZE)
    def getcurrentframe(self):
        return self.msg
    def terminate(self):
        self.term = False
        self.csocket.close()
        self.ss.close()
        



