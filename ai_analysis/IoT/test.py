from IoT import Fan_Control
fan = Fan_Control("http://192.168.0.240:7777/controller")
print(fan.get_fan_state())
while True:
    x = input("Enter 1 to turn on fan, 0 to turn off fan: ")
    fan.set_fan_state(int(x))
