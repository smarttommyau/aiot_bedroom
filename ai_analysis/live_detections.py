import numpy as np
import torch
import threading
from live_status_manager import StatusManager , AverageManagerByTime
class Person:
    def __init__(self,logger):
        self.box = None
        self.lying_bed = StatusManager(2,2)
        # self.lying_bed = StatusManager(0,0)
        self.touching_phone = StatusManager(2,2)
        # self.touching_phone = StatusManager(0,0)
        self.moving = StatusManager(2,5)
        # self.moving = StatusManager(0,0)
        self.sleeping = StatusManager(1,1)
        self.temperature = 0
        self.avgKE = AverageManagerByTime(150,30)
        # self.xyxy = torch.tensor([0,0,0,0])
        self.xyxy = None
        self.logger = logger
    ## This function must be called before other operations
    def update_box(self,box):
        self.logger.info("Person box updating...")
        self.box = box
    
    def update_lying_bed(self,bed,timenow,event):
        self.logger.info("Lying bed updating...")
        box = self.box
        xyxy = box.xyxy.flatten()
        xywh = box.xywh.flatten()
        lying_bed = False
        if bed is None:
            ## fallback to only checking posture is lying or not
            length = max(xywh[2],xywh[3])
            width = min(xywh[2],xywh[3])
            if(length/width>3 and length/width<5):
                lying_bed = None
            else:
                lying_bed = False
        else:
            ## check if the person is on the bed
            bxyxy = bed.box.xyxy.flatten()
            bxywh = bed.box.xywh.flatten()
            ## tolerance of 30 pixels
            if torch.all(xyxy[0:2] >= bxyxy[0:2] - 30) and torch.all(xyxy[2:4] <= bxyxy[2:4] + 30):
                ## check if person is lying
                if bxywh[2] > bxywh[3]:
                    if xywh[2]/bxywh[2] > 0.6:
                        lying_bed = True

                else:
                    if xywh[3]/bxywh[3] > 0.6:
                        lying_bed = True
        event.set()
        if lying_bed is not None:
            self.lying_bed.update_status(lying_bed,timenow)
    def update_touching_phone(self,phones,timenow,event):
        self.logger.info("Touching phone updating...")
        xyxy = self.box.xyxy.flatten()

        for phone in phones:
            pxyxy = phone.box.xyxy.flatten()
            ## tolerance of 10 pixels
            if torch.all(pxyxy[0:2] >= xyxy[0:2] - 10) and torch.all(pxyxy[2:4] <= xyxy[2:4] + 10):
                self.touching_phone.update_status(True,timenow)
                event.set()
                return
        self.touching_phone.update_status(False,timenow)
        event.set()
    ## AVG KE update with mving
    def update_moving(self,timenow,event):
        self.logger.info("Moving updating...")
        if self.xyxy is None:
            self.xyxy = self.box.xyxy
            event.set()
            return
        xyxy = self.box.xyxy
        # tolerance of movement is 15 pixels
        value = torch.abs(xyxy - self.xyxy)
        self.avgKE.update_value(torch.sum(value).item(),timenow)##FIXME: Thousands of bugs

        if torch.all(value < 15):
            self.moving.update_status(False,timenow)
        else:
            self.moving.update_status(True,timenow)
        self.xyxy = xyxy
        event.set()

    def update_temperature(self,thermal,other_object,event):
        self.logger.info("Temperature updating...")
        (x1,y1,x2,y2) = self.box.xyxy.flatten().long()
        other_object[thermal<30] = 0 
        other_object[thermal>40] = 0
        thermal = thermal * other_object
        self.temperature = (np.sum(thermal[x1:x2+1 , y1:y2+1])/np.sum(other_object[x1:x2+1 , y1:y2+1]))/100 - 273
        event.set()

    def update_sleeping(self,timenow,event,lying_bed,touching_phone):
        lying_bed.wait(),touching_phone.wait()
        self.logger.info("Sleeping updating...")
        sleeping = False
        if self.lying_bed.status and not self.touching_phone.status:
            sleeping = True
        self.sleeping.update_status(sleeping,timenow)
        event.set()
    ## FIXME: not able to sleep or bad sleep(exclude using phone situation)
    ## List of probale situations:
    ## 1. eyes open(hard to implement)
    ## 2. High average movement(implementation done)

class Bed:
    def __init__(self,logger):
        self.box = None
        self.temperature = 0
        self.logger = logger
    def update_box(self,box):
        self.logger.info("Bed box updating...")
        self.box = box
    def update_temperature(self,thermal,other_object,personxyxy,event):
        self.logger.info("Bed temperature updating...")
        (x1,y1,x2,y2) = self.box.xyxy.flatten().long()
        ## set overlap with person to 0
        if personxyxy is not None:
            (x1p,y1p,x2p,y2p) = personxyxy.long()
            other_object[x1p:x2p+1 , y1p:y2p+1] = 0
        thermal = thermal * other_object
        self.temperature = (np.sum(thermal[x1:x2+1 , y1:y2+1])/np.sum(other_object[x1:x2+1 , y1:y2+1]))/100 - 273
        event.set()
    

class Phone:
    def __init__(self,box):
        self.box = box
# Class for detection algorithms
class detection:
    def __init__(self,logger):
        ##TODO multi-user support by using yolo track
        self.person = Person(logger)
        self.person_presence = StatusManager(0,2)
        self.lock = threading.Lock()
        self.action_lock = []
        self.timenow = 0
        self.events = tuple(threading.Event() for _ in range(6))
        self.condition_self = threading.Condition()
        self.bed = Bed(logger)
        self.logger = logger
        ## 0: lying_bed, 1: touching_phone, 2: moving, 3: temperature, 4: bed_temperature, 5: sleep
    def update(self,result,thermal,timenow):

        ## timenow is now perserve, may still use later is fps is fluctuating too much
        # Persons = list()
        phones =  list()
        other_object = np.ones((640,480))
        boxs = None
        bboxs = None
        for box in result.boxes:
            if box.cls == 0:
                ## cannot actually does multi user
                # Persons.append(Person(box))
                if boxs is not None:
                    continue
                boxs = box
                
            elif box.cls == 59:
                bboxs = box
            elif box.cls == 63 or box.cls == 67:
                phones.append(Phone(box))
                ## set other object to 1 with box.xyxy
                (x1,y1,x2,y2) = box.xyxy.flatten().long()
                other_object[x1:x2+1 , y1:y2+1] = 0
        self.logger.info("Lock aquired")
        self.lock.acquire(blocking=True)
        for i,action in enumerate(self.action_lock):
            action.wait()
            action.clear()
        with self.condition_self:
            self.condition_self.notify_all()
        self.logger.info("Through Lock")


        for event in self.events:
            event.clear()

        self.timenow = timenow


        if boxs is not None:
            self.person.update_box(boxs)

        if bboxs is not None:
            self.bed.update_box(bboxs)
            threading.Thread(target=self.bed.update_temperature,args=(thermal,other_object,boxs.xyxy.flatten() if boxs is not None else None,self.events[4])).start()
        else:
            self.events[4].set()
            self.logger.info("No Bed!!")


        if boxs is None:
            for action_lock in self.action_lock:
                action_lock.set()
            if self.person_presence.update_status(False,timenow):
                self.person.sleeping.status = False
                self.person.touching_phone.status = False
                self.person.lying_bed.status = False
                self.person.moving.status = False
                self.person.temperature = 0
                self.events[0].set(),self.events[1].set(),self.events[2].set(),self.events[3].set(),self.events[5].set()
                self.lock.release()
                return                
            else:
                self.lock.release()
                return
        else:
            self.person_presence.update_status(True,timenow)

        # for person in Persons:
        threading.Thread(target=self.person.update_sleeping,args=(timenow,self.events[5],self.events[0],self.events[1])).start()
        threading.Thread(target=self.person.update_lying_bed,args=(self.bed if bboxs is not None else None,timenow,self.events[0])).start()
        threading.Thread(target=self.person.update_touching_phone,args=(phones,timenow,self.events[1])).start()
        threading.Thread(target=self.person.update_moving,args=(timenow,self.events[2])).start()
        threading.Thread(target=self.person.update_temperature,args=(thermal,other_object,self.events[3])).start()
        self.lock.release()
    def reset(self):
        self.logger.info("Lock aquired")
        self.lock.acquire(blocking=True)
        for i,action in enumerate(self.action_lock):
            action.wait()
            action.clear()
        with self.condition_self:
            self.condition_self.notify_all()
        self.logger.info("Through Lock")
        self.person_presence.reset()
        self.person.sleeping.reset()
        self.person.touching_phone.reset()
        self.person.lying_bed.reset()
        self.person.moving.reset()
        self.person.temperature = 0
        self.person.xyxy = None
        for event in self.events:
            event.set()
        self.lock.release()
