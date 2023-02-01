from live_connection import *
import threading

ip = input("The address to bind:")
connection = Live_connection(ip,7777)


t1 = threading.Thread(target = connection.start_connection)
t1.start()
print("100")
for i in range(10):
    while not connection.new_frame_avaliable:
        pass
    print("1000")
    (frame,thermal) = connection.getcurrentframe()
    f = open("img/test" + str(i) + ".png","wb")
    f.write(frame)
    f.close()
    f = open("img/test" + str(i) + "thermal.txt","w")
    f.write(str(thermal))
    f.close()
    print(int(thermal[int(connection.width/2)][int(connection.height/2)])/100 - 273,"\n")
    

connection.terminate()
t1.join()
