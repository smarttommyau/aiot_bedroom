from live_connection import *
from PIL import BmpImagePlugin
import threading

ip = input("The address to bind:")
connection = Live_connection(ip,7777)
connection.start_connection()

t1 = threading.Thread(connection.start_recieve())
t1.start()

while not connection.new_frame_avaliable:
    pass

frame = connection.getcurrentframe()
image = BmpImagePlugin.BmpImageFile()
image.frombytes(frame)
image.save("test.bmp")
