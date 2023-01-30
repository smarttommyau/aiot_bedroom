from live_connection import *
from PIL import BmpImagePlugin
import threading
import io

ip = input("The address to bind:")
connection = Live_connection(ip,7777)
connection.start_connection()

t1 = threading.Thread(target = connection.start_recieve)
t1.start()
print("100")
for i in range(10):
    while not connection.new_frame_avaliable:
        pass
    print("1000")
    frame = connection.getcurrentframe()
    f = open("test" + str(i) + ".png","wb")
    f.write(frame)
    f.close()

connection.terminate()
t1.join()
