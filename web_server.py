import network
import time
from led import Led

class WebServer:
    def __init__(self,pin_led=2):            
        self.led = Led(pin_led)     

    def connect_wifi(self, ssid, password):
        self.sta_if = network.WLAN(network.STA_IF)
        self.sta_if.active(False)
        time.sleep(2)
        self.sta_if.active(True)
        self.sta_if.connect(ssid, password)
        print('Conectando Wi-Fi...')
        while not self.sta_if.isconnected():
            self.led.blink()
        print('Wi-Fi conectado em:')
        print('IP: ', self.sta_if.ifconfig()[0] )
        print('Mascara: ', self.sta_if.ifconfig()[1] )
        print('GetWay: ', self.sta_if.ifconfig()[2] )
        print('DNS: ', self.sta_if.ifconfig()[0] )
        self.led.on()
    
    def close(self):       
        self.sta_if.disconnect()
        self.sta_if.active(False)
        