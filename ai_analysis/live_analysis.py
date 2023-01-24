from live_connection import Live_connection
import threading


live_connection = Live_connection(7777)

live_connection.start_connection()

t1 = threading.Thread(live_connection.start_recieve())
t1.start()

while True :
    #get data
    thermal_data = live_connection.getcurrentframe()
    #predict with model

    
