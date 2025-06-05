from machine import Pin
from time import sleep
from state import State

class LightSwitch:
    #inicialização da Classe
    def __init__(self, pin, callback=None, pull=Pin.PULL_UP):
        self.switch = Pin(pin, Pin.IN, pull)
        self.callback = callback
        self.last_state = State(1)
        
    #pressionamento switch
    def pressBTN(self, calback):    
        sleep(0.05)  # debounce
        if self.switch.value() == 0 :
            self.last_state.toggle()         
            self.last_state.value == self.switch.value()
            calback()
    
