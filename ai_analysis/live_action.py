class action:
    def __init__(self,fan,light,buzzer) -> None:
        self.fan = fan
        self.light = light
        self.buzzer = buzzer

    ## Default tolerance number
    
    ## Thread structure
    ##1. lying bed
    ##2. touching phone
    ##3. moving
    ##4. person temperature
    ##5. bed temperature(it can be None)
    def update(self,detection,threads,timenow):
        # some denpendent states(sleeping)
        # some tolerancy states
        # call actions