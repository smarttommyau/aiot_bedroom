import threading
class action:
    def __init__(self,fan,aircon,light,detection) -> None:
        self.fan       = fan
        self.aricon    = aircon
        self.light     = light
        self.events    = detection.events
        self.detection = detection
        self.drlock    = detection.lock
        self.person    = detection.person
        self.condition = detection.condition_self
        # self.buzzer = buzzer

    def fan(self,lying,temperature,bed_temperature):
        while True:
            self.drlock.aquire(blocking=False)
            self.condition.wait()
            lying.wait(),temperature.wait(),bed_temperature.wait()
            if not self.person.lying_bed.status:
                self.fan.off()
                self.aricon.off()
                self.rlock.release()
                continue
            if self.detection.bed is None:
                self.rlock.release()
                continue
            

              
    ## Thread structure
    ##1. lying bed
    ##2. touching phone
    ##3. moving
    ##4. person temperature
    ##5. bed temperature(it can be None)

    ## Actions(depends)
    ##1. fan/aircon(body temp,bed temp(maybe none),lying)
    ##2. light(sleep,touchphone)
    ##3. callambulance(moving or body temp)
    ##4. music(lying)
        
        



    