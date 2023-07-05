from time import time
from collections import deque
from statistics import mean
class StatusManager:
    ## Tolerance to prevent false negative or false positive
    def __init__(self,tolerances_positive=0,tolerance_negative=0,status=False) -> None:
        self.__default_tolerance_positive = tolerances_positive## to become positive
        self.__default_tolerance_negative = tolerance_negative## to become negative
        self.__counter_tolerance_positive = tolerances_positive
        self.__counter_tolerance_negative = tolerance_negative
        self.status  = status
        self.start = 0
        self.end = 0
    def update_status(self,status,timenow) -> bool:
        if status == self.status:
            self.__counter_tolerance_positive = self.__default_tolerance_positive
            self.__counter_tolerance_negative = self.__default_tolerance_negative
            return False
        if status:
            self.__counter_tolerance_negative -= 1
            if self.__counter_tolerance_negative <=0:
                self.status = True
                self.end = timenow
                return True
        else:
            self.__counter_tolerance_positive -= 1
            if self.__counter_tolerance_positive <=0:
                self.status = False
                self.start = timenow
                return True
        return False

class AverageManagerByValue:
    # deque seems to have a significant edge against list 
    def __init__(self,numOf_value=10) -> None:
        self.__deque = deque(maxlen=numOf_value)
        self.average = 0
        self.__numOf_value = numOf_value
    def update_value(self,value):
        self.__deque.append(value)
        self.average = sum(self.__deque)/self.__numOf_value

#     self._target(*self._args, **self._kwargs)
#   File "D:\my programs\python\Aiot\aiot_bedroom\ai_analysis\live_detections.py", line 74, in update_moving
#     self.avgKE.update_value(torch.sum(value),timenow)
#   File "D:\my programs\python\Aiot\aiot_bedroom\ai_analysis\live_status_manager.py", line 59, in update_value
#     x = mean(self.__list)
#   File "C:\Users\Tommy AU\.conda\envs\myenv\lib\statistics.py", line 329, in mean
#     T, total, count = _sum(data)
#   File "C:\Users\Tommy AU\.conda\envs\myenv\lib\statistics.py", line 188, in _sum
#     for n, d in map(_exact_ratio, values):
#   File "C:\Users\Tommy AU\.conda\envs\myenv\lib\statistics.py", line 261, in _exact_ratio
#     raise TypeError(msg)
# TypeError: can't convert type 'Tensor' to numerator/denominator
class AverageManagerByTime:
    ## Use list as it has better stability while they have similar performance even in scale
    def __init__(self,period=60,least_item=10) -> None:
        self.__list = []
        self.__list_time = []
        self.average = 0
        self.__period = period
        self.__least_item = least_item
    def update_value(self,value,timenow):
        self.__list.append(value)
        self.__list_time.append(timenow)
        while self.__list_time[0] < timenow - self.__period:
            self.__list_time.pop(0)
            self.__list.pop(0)
        if len(self.__list) >= self.__least_item:
            x = mean(self.__list)
        else:
            x = sum(self.__list)/self.__least_item