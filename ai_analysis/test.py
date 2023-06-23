from live_connection import *
import threading
import time
from sys import exit  

ip = input("The address to bind:")
connection = Live_connection(ip,7777)


t1 = threading.Thread(target = connection.start_connection)
t1.start()
start = time.time()
print("100")
for i in range(10):
    while not connection.new_frame_avaliable:
        pass
    now = time.time()
    print("new",now-start)
    start = now
    (frame,thermal) = connection.getcurrentframe()
    with open('img/test' + str(i) + '.png', 'wb') as f:
        f.write(frame)
    with open('img/test' + str(i) + '.txt', 'wb') as f:
        np.save(f, thermal)
    print(int(thermal[int(connection.height/2)][int(connection.width/2)])/100 - 273,"\n")
    

connection.terminate()
exit(0)
