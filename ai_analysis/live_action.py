import threading
    ## Thread structure
    ##1. lying bed
    ##2. touching phone
    ##3. moving
    ##4. person temperature
    ##5. bed temperature(it can be None)
    ##6. sleeping

    ## Actions(depends)
    ##1. fan/aircon(body temp,bed temp(maybe none),lying)
    ##2. light(sleep,touchphone)
    ##3. callambulance(moving or body temp)
    ##4. music(lying)
class action:
    def __init__(self,aircon,light,detection) -> None:
        self.aricon    = aircon
        self.light     = light
        self.events    = detection.events
        self.detection = detection
        self.rlock    = detection.lock
        self.person    = detection.person
        self.condition = detection.condition_self
        # self.buzzer = buzzer
        ## Start all actions
        threading.Thread(target=self.Aircon,args=(self.events[0],self.events[3],self.events[4]))

    def Aircon(self,lying,temperature,bed_temperature):
        while True:
            self.rlock.aquire(blocking=False)
            self.condition.wait()
            lying.wait(),bed_temperature.wait()#,temperature.wait()
            if not self.person.lying_bed.status:
                self.aricon.Power(False)
                self.rlock.release()
                continue
            else:
                self.aricon.power(True)
            if self.detection.bed is None:
                self.rlock.release()
                continue
            #TODO:  bias on human temp and environment temp
                # ideal bed temp is betweeen 27 - 31
                # body temp is 36
            if self.detection.bed.temperature < 27:
                self.aricon.temp_change(+1)
            elif self.detection.bed.temperature > 31:
                self.aricon.temp_change(-1)





              

        
        



    