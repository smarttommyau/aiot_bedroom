import threading
from audioplayer import AudioPlayer
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
    def __init__(self,aircon,light,ambulance,detection,logger) -> None:
        self.aircon    = aircon
        self.light     = light
        self.ambulance = ambulance
        self.events    = detection.events
        self.detection = detection
        self.person    = detection.person
        self.logger    = logger
        for i in range(4):
            detection.action_lock.append(threading.Event())
        self.action_lock = detection.action_lock
        for action in detection.action_lock:
            action.set()
        # self.buzzer = buzzer
        ## Start all actions
        
        threading.Thread(target=self.Aircon,args=(self.events[0],self.events[3],self.events[4])).start()
        threading.Thread(target=self.Light,args=(self.events[5],self.events[1])).start()
        threading.Thread(target=self.Ambulance,args=(self.events[2],self.events[3])).start()
        threading.Thread(target=self.Music,args=(self.events[0],)).start()

    def Aircon(self,lying,temperature,bed_temperature):
        while True:
            lying.wait(),bed_temperature.wait()#,temperature.wait()
            self.logger.info("Aircon updating...")
            if not self.detection.person_presence.status or not self.person.lying_bed.status:
                self.aircon.power(False)
                self.action_lock[0].set()
                continue
            else:
                self.aircon.power(True)
            if self.detection.bed is None:
                self.action_lock[0].set()
                continue
            #TODO:  bias on human temp and environment temp
                # ideal bed temp is betweeen 27 - 31
                # body temp is 36
            if self.detection.bed.temperature < 27:
                self.aircon.temp_change(+1)
            elif self.detection.bed.temperature > 31:
                self.aircon.temp_change(-1)
            self.action_lock[0].set()
    def Light(self,sleep,touching_phone):
        while True:
            sleep.wait(),touching_phone.wait()
            self.logger.info("Light updating...")
            if not self.detection.person_presence.status:
                self.light.set_light_state(False)
                self.action_lock[1].set()
                continue
            if self.person.sleeping.status and not self.person.touching_phone.status:
                self.light.set_light_state(False)
            else:
                self.light.set_light_state(True)
            self.action_lock[1].set()
    def Ambulance(self,moving,temperature):
        while True:
            moving.wait(),temperature.wait()
            self.logger.info("Ambulance updating...")
            if not self.detection.person_presence.status:
                self.ambulance.power(False)
                self.action_lock[2].set()                
                continue
            if self.person.temperature >40 or self.person.temperature < 30:
                self.ambulance.power(True)
                self.action_lock[2].set()
            # not moving for 20 seconds
            if not self.person.moving.status and self.person.moving.start -self.detection.timenow > 20:
                self.ambulance.power(True)
                self.action_lock[2].set()
                continue
            self.ambulance.power(False)
            self.action_lock[2].set()
    def Music(self,lying):
        music_player = AudioPlayer('music/Chopin_Nocturne_E_Flat_Major_Op9_No2.mp3')
        playing = False
        # lying time >5
        while True:
            lying.wait()
            self.logger.info("Music updating...")
            if not self.detection.person_presence.status:           
                if playing:
                    music_player.stop()  
                self.action_lock[3].set() 
                continue
            if self.person.lying_bed.status and self.person.lying_bed.start -self.detection.timenow > 5:
                if not playing:
                    music_player.play(block=False)
            elif not self.lying_bed.status and self.person.lying_bed.end -self.detection.timenow > 5 and playing:
                music_player.stop() 
            self.action_lock[3].set()  

