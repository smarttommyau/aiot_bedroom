import numpy as np
class Person:
    def __init__(self,box):
        self.box = box
        self.lying_bed = False
    def update_lying_bed(self,bed):
        if(bed is None):
            ## fallback to only checking posture is lying or not
            length = max(box.x)



class Bed:
    def __init__(self,box):
        self.box = box
# Class for detection algorithms
class detection:
    def __init__(self):
        pass
    def update(self,result,thermal,timenow):
        Persons = list()
        bed = None
        for box in result.boxes:
            if box.cls == 0:
                Persons.append(Person(box))
            elif box.cls == 59:
                bed = Bed(box)
        for person in Persons:






        
# State variables
##global tolerance
    tolerance = 10
## Person exist
    personexist = False
## lying bed
    lyingonbed = False
    startlyingtime = 0
    notlyingtimestart = 0
    chancelying = 3
## touching phone
    Touchingphone = False
    starttouchingtime = 0
    nottouchingtimestart = 0
    chanceTouching = 3
## sleeping
    sleeping = False
    startsleepingtime = 0
    notsleepingtimestart = 0
## not moving
    notmoving = False
    lastposition = [0,0,0,0]
    toleranceOfNotMoving = 10
    startnotmovingtime = 0
    movingtimestart = 0
    chancenotmoving = 2
## temperatures
    tempPerson = []
### core temp requires face recongnition
    tempBed = -1
# Detection algorithms
# TODO: Update for multi-user

## Person
    def isPersonAvailable(self)-> bool:
        return 0 in pandas['class'].array

## Bed lying
    def isLyinOnBed(self,k:int)->bool:
        #pandasDataFrame is the output of model(pandas.DataFrame)
        #return true if the person is lying on the bed
        #return false if the person is not lying on the bed

        # Check if the person is on bed     
        if not(0 in pandas['class'].array):
            return False
        # Calculate the length ratio of person on the bed
        personxlen = pandas[pandas['class'] == 0]['xmax'].array[k] - pandas[pandas['class'] == 0]['xmin'].array[k]
        personylen = pandas[pandas['class'] == 0]['ymax'].array[k] - pandas[pandas['class'] == 0]['ymin'].array[k]
        if not(59 in pandas['class'].array):
            if personylen>personxlen:
                if(personylen/personxlen>3 and personylen/personxlen<5):# acoording to web data, the ratio of length to  shoulder is 4:1
                    return True
                else:
                    return False
        bedxlen = pandas[pandas['class'] == 59]['xmax'].array[0] - pandas[pandas['class'] == 59]['xmin'].array[0]
        bedylen = pandas[pandas['class'] == 59]['ymax'].array[0] - pandas[pandas['class'] == 59]['ymin'].array[0]

        if bedxlen > bedylen :
                return personxlen/bedxlen > 0.6
        else:
                return personylen/bedylen > 0.6

## Phone touching
    def isTouchingPhone(pandas,person)->bool:
        #pandasDataFrame is the output of model(pandas.DataFrame)
        #return true if the person is touching the phone
        #return false if the person is not touching the phone
        #return None if the person is not in the frame
        # Check if the person is on bed
        phone = []
        if 63 in pandas['class'].array:
            phone.append(pandas[pandas['class'] == 63])
        if 67 in pandas['class'].array:
            phone.append(pandas[pandas['class'] == 67])
        if len(phone) == 0:
            return False
        # see if the person touches the phone
        overlapArea = 0
        people = pandas[pandas['class'] == 0]
        for x in person:
            for y in phone:
                for z in range(len(y)):
                    x_overlap = max(0, min(y['xmax'].array[z], people['xmax'].array[x]) - max(y['xmin'].array[z], people['xmin'].array[x]));
                    y_overlap = max(0, min(y['ymax'].array[z], people['ymax'].array[x]) - max(y['ymin'].array[z], people['ymin'].array[x]));
                    overlapArea = max(overlapArea,x_overlap * y_overlap);
                    areaphone = (y['xmax'].array[z] - y['xmin'].array[z])*(y['ymax'].array[z] - y['ymin'].array[z])
                    time.sleep(1)
                    if overlapArea/areaphone > 0.3:
                        return True
        return False



