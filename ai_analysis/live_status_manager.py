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
                self.status = False
                self.end = timenow
                return True
        else:
            self.__counter_tolerance_positive -= 1
            if self.__counter_tolerance_positive <=0:
                self.status = True
                self.start = timenow
                return True

            