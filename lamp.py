from relay import Relay
from state import State


class Lamp:
    def __init__(self, pin_relay1, pin_relay2):
        self.phase_1 = Relay(pin_relay1)
        self.phase_2 = Relay(pin_relay2)
        self.state = State(0)        

    def on(self):
        self.state.on()
        self.phase_1.on()
        self.phase_2.on()
        self._alerta("Ligada")

    def off(self):
        self.state.off()
        self.phase_1.off()
        self.phase_2.off()
        self._alerta("Desligada")

    def toggle(self):
        if self.state.value:
            self.off()
        else:
            self.on()

    
