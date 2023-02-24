import requests

class Fan_Control:
    def __init__(self,url:str):
        self.url = url
    def get_fan_state(self) -> bool:
        params = {"fan":"State"}
        result = requests.get(url = self.url,params=params)
        return result.text=="On"
    def set_fan_state(self,state:bool) -> bool:
        params = {"fan":"On"if state else "Off"}
        result = requests.get(url = self.url,params=params)
        if(result.status_code == 200):
            return True
        else:
            return False
        
class Light_Control:
    def __init__(self,url:str):
        self.url = url
    def get_light_state(self) -> bool:
        params = {"light":"State"}
        result = requests.get(url = self.url,params=params)
        return result.text=="On"
    def set_light_state(self,state:bool) -> bool:
        params = {"light":"On"if state else "Off"}
        result = requests.get(url = self.url,params=params)
        if(result.status_code == 200):
            return True
        else:
            return False
class Buzzer_Control:
    def __init__(self,url:str):
        self.url = url
    def send_buzzer_command(self,frequency:int,duration:int) -> bool:
        params = {"buzzer":"","buzzer-freq":frequency,"buzzer-dur":duration}
        result = requests.get(url = self.url,params=params)
        if(result.status_code == 200):
            return True
        else:
            return False