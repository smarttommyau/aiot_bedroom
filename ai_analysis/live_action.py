import threading
from audioplayer import AudioPlayer
from live_status_manager import StatusManager
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
    def __init__(self,aircon,light,ambulance,caring,detection,logger) -> None:
        self.aircon    = aircon
        self.light     = light
        self.ambulance = ambulance
        self.caring    = caring
        self.__ambulance_temperture = StatusManager(4,2)
        self.__ambulance_moving = StatusManager(4,2)
        self.events    = detection.events
        self.detection = detection
        self.person    = detection.person
        self.logger    = logger
        self.main_lock = detection.condition_self
        for _ in range(5):
            detection.action_lock.append(threading.Event())
        self.action_lock = detection.action_lock
        # self.buzzer = buzzer
        ## Start all actions
        
        threading.Thread(target=self.Aircon,args=(self.events[0],self.events[3],self.events[4])).start()
        threading.Thread(target=self.Light,args=(self.events[5],)).start()
        threading.Thread(target=self.Ambulance,args=(self.events[2],self.events[3],self.events[1])).start()
        threading.Thread(target=self.Music,args=(self.events[0],)).start()
        threading.Thread(target=self.Caring,args=(self.events[2],self.events[5])).start()

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
            #future:  bias on human temp and environment temp
                # ideal bed temp is betweeen 27 - 31
                # body temp is 36
                # Need to be implement carefully
            ## future:Aircon change with function to determine the magnitude of change
            if self.detection.bed.temperature < 27:
                self.aircon.temp_change(+1)
            elif self.detection.bed.temperature > 31:
                self.aircon.temp_change(-1)
    def Light(self,sleep):
        self.logger.info("Light action started")
        while True:
            self.action_lock[1].set()
            with self.main_lock:
                self.main_lock.wait()
            sleep.wait()
            self.logger.info("Light updating...")
            if not self.detection.person_presence.status:
                self.logger.info("Light updating... no person")
                self.light.set_light_state(False)
                continue
            if self.person.sleeping.status and self.detection.timenow - self.person.sleeping.start > 5:
                self.logger.info("Light updating... sleeping")
                self.light.set_light_state(False)
            elif not self.person.sleeping.status and self.detection.timenow - self.person.sleeping.end > 5:
                self.logger.info("Light updating... not sleeping")
                self.light.set_light_state(True)
    def Ambulance(self,moving,temperature,lying):
        self.logger.info("Ambulance action started")
        while True:
            self.action_lock[2].set()                
            with self.main_lock:
                self.main_lock.wait()
            moving.wait(),temperature.wait(),lying.wait()
            self.logger.info("Ambulance updating...")
            if not self.detection.person_presence.status:
                self.ambulance.power(False)
                self.__ambulance_temperture.update_status(False,self.detection.timenow)
                continue
            if self.person.temperature >40 or self.person.temperature < 30:
                self.__ambulance_temperture.update_status(True,self.detection.timenow)
            else:
                self.__ambulance_temperture.update_status(False,self.detection.timenow)
            if self.__ambulance_temperture.status and self.detection.timenow - self.__ambulance_temperture.start > 20:
                self.ambulance.power(True)
                continue
            # not moving for 20 seconds
            if not self.person.moving.status and not self.person.lying_bed.status:
                self.__ambulance_moving.update_status(True,self.detection.timenow)
            else:
                self.__ambulance_moving.update_status(False,self.detection.timenow)
            if self.__ambulance_moving.status and self.detection.timenow - self.__ambulance_moving.start > 20:
                self.ambulance.power(True)
                continue
            self.ambulance.power(False)
    def Music(self,lying):
        ##future: real music player
        ##TODO: Music player class
        ## 1. able to select music
        ## 2. support playlist
        ## 3. rich functions(extra window to control?)
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
            if self.person.lying_bed.status and self.detection.timenow - self.person.lying_bed.start > 5:
                if not playing:
                    music_player.play(block=False,loop = True)
            elif not self.person.lying_bed.status and self.detection.timenow - self.person.lying_bed.end > 5 and playing:
                music_player.stop() 

## FIXME: elederly func
## FIXME: care service(lower class of ambulance)
# work flow
# first connect to service center
# then let human check if its the case
# last let human start talk with the patient
## FIXME: care service(mock implementation)
## FIXME: using the data of average KE
    def Caring(self,move,sleep):
        self.logger.info("Caring action started")
        while True:
            self.action_lock[4].set() 
            with self.main_lock:
                self.main_lock.wait()
            move.wait(),sleep.wait()
            self.logger.info("Caring updating...")
            if not self.detection.person_presence.status:
                self.caring.power(False)
                continue
            ## By some unknown source. It claims that human flip once in 30 min when sleep
            ## With high values, it should be bad sleep or not able to sleep
            if self.person.EffectiveMoves.counter > 4 and self.person.sleeping.status: ##and self.detection.timenow - self.person.sleeping.start > 30:
                self.caring.power(True)
                self.logger.info("Caring updating... start caring")
            else:
                self.caring.power(False)
                self.logger.info("Caring updating... stop caring")
    

