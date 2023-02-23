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
        