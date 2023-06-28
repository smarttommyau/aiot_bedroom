import numpy as np
import torch
import threading
class Person:
    def __init__(self):
        self.box = None
        self.lying_bed = False
        self.touching_phone = False
        self.temperature = 0
        self.xyxy = torch.tensor([0,0,0,0])
        self.moving = False
        self.notmoving = 0
    ## This function must be called before other operations
    def update_box(self,box):
        self.box = box

    def update_lying_bed(self,bed):
        box = self.box
        self.lying_bed = False
        if(bed is None):
            ## fallback to only checking posture is lying or not
            length = max(box.xywh[2],box.xywh[3])
            width = min(box.xywh[2],box.xywh[3])
            if(length/width>3 and length/width<5):
                self.lying_bed = True
        else:
            ## check if the person is on the bed
            if torch.all(box.xyxy[0:2] >= bed.box.xyxy[0:2]) and torch.all(box.xyxy[2:4] <= bed.box.xyxy[2:4]):
                ## check if person is lying
                if bed.box.xywh[2] > bed.box.xywh[3]:
                    if box.xywh[2]/box.xywh[3] > 0.6:
                        self.lying_bed = True
                else:
                    if box.xywh[3]/box.xywh[2] > 0.6:
                        self.lying_bed = True
    def update_touching_phone(self,phones):
        box = self.box
        self.touching_phone = False
        for phone in phones:
            if torch.all(phone.box.xyxy[0:2] >= box.xyxy[0:2]) and torch.all(phone.box.xyxy[2:4] <= box.xyxy[2:4]):
                self.touching_phone = True
                return
    def update_moving(self):
        # tolerance of movement is 10 pixels
        xyxy = self.box.xyxy
        if torch.all(torch.abs(self.xyxy-xyxy)<10):
            self.moving = False
            self.notmoving += 1
        else:
            self.moving = True
        self.xyxy = xyxy

    def update_temperature(self,thermal,other_object):
        (x1,y1,x2,y2) = self.box.xyxy
        thermal = thermal * other_object
        self.temperature = np.sum(thermal[x1:x2+1][y1:y2+1]/100 - 273)/(x2-x1+1)/(y2-y1+1)




class Bed:
    def __init__(self,box):
        self.box = box
    def update_temperature(self,thermal,other_object,personxyxy):
        (x1,y1,x2,y2) = self.box.xyxy
        thermal = thermal * other_object
        ## set overlap with person to 0
        (x1p,y1p,x2p,y2p) = personxyxy
        thermal[x1p:x2p+1][y1p:y2p+1] = 0
        self.temperature = np.sum(thermal[x1:x2+1][y1:y2+1]/100 - 273)/(x2-x1+1)/(y2-y1+1)
    

class Phone:
    def __init__(self,box):
        self.box = box
# Class for detection algorithms
class detection:
    def __init__(self):
        self.person = Person()
        self.lock = False
    def update(self,result,thermal) -> list[threading.Thread]:
        ## timenow is now perserve, may still use later is fps is fluctuating too much
        # Persons = list()
        while self.lock:
            pass
        self.lock = True
        phones =  list()
        bed = None
        updated = False
        other_object = np.ones((640,480))
        for box in result.boxes:
            if box.cls == 0:
                ## cannot actually does multi user
                # Persons.append(Person(box))
                if updated:
                    pass
                self.person.update_box(box)
                updated = True
                
            elif box.cls == 59:
                bed = Bed(box)
            elif box.cls == 63 or box.cls == 67:
                phones.append(Phone(box))
                ## set other object to 1 with box.xyxy
                (x1,y1,x2,y2) = box.xyxy
                other_object[x1:x2+1][y1:y2+1] = 0
        # for person in Persons:
        threads = tuple(
            threading.Thread(target=self.person.update_lying_bed,args=(bed,)),
            threading.Thread(target=self.person.update_touching_phone,args=(phones,)),
            threading.Thread(target=self.person.update_moving,args=()),
            threading.Thread(target=self.person.update_temperature,args=(thermal,other_object))
            threading.Thread(target=box.update_temperature,args=(thermal,other_object,person.box.xyxy))
        )
        for thread in threads:
            thread.start()
        return threads
    def free(self):
        self.lock = False