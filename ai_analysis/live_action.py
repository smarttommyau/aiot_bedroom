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
    ##3. callambulance(moving or body temp,lying)
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
        self.main_lock = detection.condition_self
        for _ in range(4):
            detection.action_lock.append(threading.Event())
        self.action_lock = detection.action_lock
        # self.buzzer = buzzer
        ## Start all actions
        
        threading.Thread(target=self.Aircon,args=(self.events[0],self.events[3],self.events[4])).start()
        threading.Thread(target=self.Light,args=(self.events[5],self.events[1])).start()
        threading.Thread(target=self.Ambulance,args=(self.events[2],self.events[3],self.events[1])).start()
        threading.Thread(target=self.Music,args=(self.events[0],)).start()

    def Aircon(self,lying,temperature,bed_temperature):
        self.logger.info("Aircon action started")
        while True:
            self.action_lock[0].set()
            with self.main_lock:
                self.main_lock.wait()
            lying.wait(),bed_temperature.wait()#,temperature.wait()
            self.logger.info("Aircon updating...")
            if not self.detection.person_presence.status or not self.person.lying_bed.status:
                self.aircon.power(False)
                continue
            else:
                self.aircon.power(True)
            if self.detection.bed is None:
                continue
            #TODO:  bias on human temp and environment temp
                # ideal bed temp is betweeen 27 - 31
                # body temp is 36
            ## TODO:Aircon change with function to determine the magnitude of change
            if self.detection.bed.temperature < 27:
                self.aircon.temp_change(+1)
            elif self.detection.bed.temperature > 31:
                self.aircon.temp_change(-1)
    def Light(self,sleep,touching_phone):
        ##FIXME: Testing
        self.logger.info("Light action started")
        while True:
            self.action_lock[1].set()
            with self.main_lock:
                self.main_lock.wait()
            sleep.wait(),touching_phone.wait()
            self.logger.info("Light updating...")
            if not self.detection.person_presence.status:
                self.light.set_light_state(False)
                continue
            if self.person.sleeping.status and not self.person.touching_phone.status:
                self.light.set_light_state(False)
            else:
                self.light.set_light_state(True)
    def Ambulance(self,moving,temperature,lying):
        ## FIXME: Testing
        self.logger.info("Ambulance action started")
        while True:
            self.action_lock[2].set()                
            with self.main_lock:
                self.main_lock.wait()
            moving.wait(),temperature.wait(),lying.wait()
            self.logger.info("Ambulance updating...")
            if not self.detection.person_presence.status:
                self.ambulance.power(False)
                continue
            if self.person.temperature >40 or self.person.temperature < 30:
                self.ambulance.power(True)
            # not moving for 20 seconds
            if not self.person.moving.status and self.person.moving.start -self.detection.timenow > 20 and not self.person.lying_bed.status:
                self.ambulance.power(True)
                continue
            self.ambulance.power(False)
    def Music(self,lying):
        ## FIXME: Testing
        self.logger.info("Music action started")
        music_player = AudioPlayer('music/Chopin_Nocturne_E_Flat_Major_Op9_No2.mp3')
        playing = False
        # lying time >5
        while True:
            self.action_lock[3].set() 
            with self.main_lock:
                self.main_lock.wait()
            lying.wait()
            self.logger.info("Music updating...")
            if not self.detection.person_presence.status:           
                if playing:
                    music_player.stop()  
                continue
            if self.person.lying_bed.status and self.person.lying_bed.start -self.detection.timenow > 5:
                if not playing:
                    music_player.play(block=False)
            elif not self.person.lying_bed.status and self.person.lying_bed.end -self.detection.timenow > 5 and playing:
                music_player.stop() 

## FIXME: elederly func
