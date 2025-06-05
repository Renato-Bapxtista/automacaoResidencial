import dht
from machine import Pin

class DHT11Sensor:
    def __init__(self, pin):
        self.sensor = dht.DHT11(Pin(pin))

    def ler(self):
        try:
            self.sensor.measure()
            temperatura = self.sensor.temperature()
            umidade = self.sensor.humidity()
            return {
                'temperatura': temperatura,
                'umidade': umidade
            }
        except Exception as e:
            print("Erro na leitura DHT11:", e)
            return {
                'temperatura': None,
                'umidade': None
            }
