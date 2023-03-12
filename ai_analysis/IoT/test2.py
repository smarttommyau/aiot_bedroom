from IoT import Light_Control,Fan_Control,Buzzer_Control
from time import sleep
url = "http://192.168.0.240:7777/controller"

fan = Fan_Control(url)
light = Light_Control(url)
buzzer = Buzzer_Control(url)

while True:
    light.set_light_state(True)
    fan.set_fan_state(True)
    buzzer.send_buzzer_command(1000,1000)
    sleep(1.5)
    light.set_light_state(False)
    fan.set_fan_state(False)
    buzzer.send_buzzer_command(1000,1000)