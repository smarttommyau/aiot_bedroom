from IoT import *
from time import sleep
tones = {
"B0": 31,
"C1": 33,
"CS1": 35,
"D1": 37,
"DS1": 39,
"E1": 41,
"F1": 44,
"FS1": 46,
"G1": 49,
"GS1": 52,
"A1": 55,
"AS1": 58,
"B1": 62,
"C2": 65,
"CS2": 69,
"D2": 73,
"DS2": 78,
"E2": 82,
"F2": 87,
"FS2": 93,
"G2": 98,
"GS2": 104,
"A2": 110,
"AS2": 117,
"B2": 123,
"C3": 131,
"CS3": 139,
"D3": 147,
"DS3": 156,
"E3": 165,
"F3": 175,
"FS3": 185,
"G3": 196,
"GS3": 208,
"A3": 220,
"AS3": 233,
"B3": 247,
"C4": 262,
"CS4": 277,
"D4": 294,
"DS4": 311,
"E4": 330,
"F4": 349,
"FS4": 370,
"G4": 392,
"GS4": 415,
"A4": 440,
"AS4": 466,
"B4": 494,
"C5": 523,
"CS5": 554,
"D5": 587,
"DS5": 622,
"E5": 659,
"F5": 698,
"FS5": 740,
"G5": 784,
"GS5": 831,
"A5": 880,
"AS5": 932,
"B5": 988,
"C6": 1047,
"CS6": 1109,
"D6": 1175,
"DS6": 1245,
"E6": 1319,
"F6": 1397,
"FS6": 1480,
"G6": 1568,
"GS6": 1661,
"A6": 1760,
"AS6": 1865,
"B6": 1976,
"C7": 2093,
"CS7": 2217,
"D7": 2349,
"DS7": 2489,
"E7": 2637,
"F7": 2794,
"FS7": 2960,
"G7": 3136,
"GS7": 3322,
"A7": 3520,
"AS7": 3729,
"B7": 3951,
"C8": 4186,
"CS8": 4435,
"D8": 4699,
"DS8": 4978,
"P":0
}
url = "http://192.168.0.240:7777/controller"
#update url if you want
x = input("Input url(keep default by null): ")
if x != "":
    url = x
while True:
    # select device to control
    xs = input("Enter 1 to control fan, 2 to control light, 3 to control buzzer, 4 to exit: ")
    if xs == "4":
        break
    if xs == "1":
        fan = Fan_Control(url)
        print(fan.get_fan_state())
        while True:
            x = input("Enter 1 to turn on fan, 0 to turn off fan,2 to exit: ")
            if x == "2":
                break
            fan.set_fan_state(int(x))
    if xs == "2":
        light = Light_Control(url)
        print(light.get_light_state())
        while True:
            x = input("Enter 1 to turn on light, 0 to turn off light,2 to exit: ")
            if x == "2":
                break
            light.set_light_state(int(x))
    if xs == "3":
        buzzer = Buzzer_Control(url)
        while True:
            x = input("Enter frequency and duration to send buzzer command\n,2 to exit\n,3 to play interesting music: ")
            if x == "2":
                break
            if x == "3":
                # twinkle twinkle little star
                song = ["C5","C5","G5","G5","A5","A5","G5","P","F5","F5","E5","E5","D5","D5","C5","P","G5","G5","F5","F5","E5","E5","D5","P","C5","C5","G5","G5","A5","A5","G5","P","F5","F5","E5","E5","D5","D5","C5","P"]
                for x in song:
                    buzzer.send_buzzer_command(tones[x],500)
                    sleep(0.5)
                continue 
            x = x.split()
            buzzer.send_buzzer_command(int(x[0]),int(x[1]))