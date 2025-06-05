from machine import ADC, Pin
from time import sleep
import urequests

class MQ2Sensor:
    def __init__(self, pin_adc, pin_digital=None, alerta_pin=None, api_key=None, numero=None):
        self.adc = ADC(Pin(pin_adc))
        self.adc.atten(ADC.ATTN_11DB)

        self.digital_pin = Pin(pin_digital, Pin.IN) if pin_digital is not None else None
        self.alerta = Pin(alerta_pin, Pin.OUT) if alerta_pin is not None else None
        self.api_key = api_key
        self.numero = numero

    def ler_gas(self):
        valor = self.adc.read()
        ppm = (valor / 4095) * 10000
        return round(ppm, 2)

    def ler_digital(self):
        if self.digital_pin:
            return self.digital_pin.value()
        else:
            return None

    def verificar_alerta(self):
        ppm = self.ler_gas()
        digital = self.ler_digital()

        if digital == 1:
            nivel = "Emergência(Digital)"
            self._ligar_alerta()
            #self._enviar_whatsapp(ppm, nivel)        

        elif ppm < 400:
            nivel = "Seguro"
            self._desligar_alerta()

        elif 400 <= ppm < 1000:
            nivel = "Atenção"
            self._piscar_alerta(0.5)
            #self._enviar_whatsapp(ppm, nivel)

        elif 1000 <= ppm < 5000:
            nivel = "Perigo"
            self._piscar_alerta(0.2)
            #self._enviar_whatsapp(ppm, nivel)

        else:  # >=5000
            nivel = "Emergência"
            self._ligar_alerta()
            #self._enviar_whatsapp(ppm, nivel)

        return {"ppm": ppm, "nivel": nivel, "alerta_whatsapp": "on" if digital == 1 else "off"}

    def _ligar_alerta(self):
        if self.alerta:
            self.alerta.value(1)

    def _desligar_alerta(self):
        if self.alerta:
            self.alerta.value(0)

    def _piscar_alerta(self, tempo):
        if self.alerta:
            self.alerta.value(1)
            sleep(tempo)
            self.alerta.value(0)
            sleep(tempo)

    def _enviar_whatsapp(self, ppm, nivel):
        if self.api_key and self.numero:
            mensagem = f"🚨 ALERTA DE GAS NA COZINHA 🚨%0APPM: {ppm}%0ANivel: {nivel}"
            try:
                url = f"https://api.callmebot.com/whatsapp.php?phone={self.numero}&text={mensagem}&apikey={self.api_key}"
                r = urequests.get(url)
                r.close()
            except:
                print("Erro no envio WhatsApp")
