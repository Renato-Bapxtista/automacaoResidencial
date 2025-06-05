#imports
from machine import ADC, Pin, SoftI2C
from time import sleep
#from state import State

####################################################################

#classemresponsavel por leitura do sensor DHT11
#imports da classe
import dht

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
################################################################################################

#classemresponsavel por gerenciamento de uma lampada bifase sem neutro
#imports da classe
#from relay import Relay


class Lamp:
    def __init__(self, pin_relay1, pin_relay2):
        self.phase_1 = Relay(pin_relay1)
        self.phase_2 = Relay(pin_relay2)
        self.state = State(0)        

    def on(self):
        self.state.on()
        self.phase_1.on()
        self.phase_2.on()        

    def off(self):
        self.state.off()
        self.phase_1.off()
        self.phase_2.off()
        
    def toggle(self):
        if self.state.value:
            self.off()
        else:
            self.on()
#####################################################################################################
#classemresponsavel polo gerenciamento de um led
#imports da classe

class Led:
    def __init__(self, pin):
        self.led = Pin(pin, Pin.OUT)
        self.state = 0
        self.led.value(self.state)

    def on(self):
        self.state = 1
        self.led.value(self.state)

    def off(self):
        self.state = 0
        self.led.value(self.state)

    def toggle(self):
        self.state = not self.state
        self.led.value(self.state)

    def blink(self):
        self.toggle()
        sleep(0.3)
####################################################################################################
#classe responsavel pelo gerenciamento de botao
#imports da classe

class LightSwitch1:
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
###########################################################################################################
#classe responsavel pelo gerenciamento de tecla Parede
#imports da classe

class LightSwitch2:
    #inicialização da Classe
    def __init__(self, pin, callback=None, pull=Pin.PULL_UP):
        self.switch = Pin(pin, Pin.IN, pull)
        self.callback = callback
        self.last_state = State(1)
        
    #pressionamento switch
    def pressBTN(self, callback):    
        sleep(0.05)  # debounce
        
        if self.switch.value() != self.last_state.value:            
            self.last_state.toggle()
            callback()
            
            
#########################################################################################################
#classe responsavel pela leitura de um sensor MQ2
#imports da classe
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
########################################################################################################################
#classe responsavel pelo gerenciamento de um rele
#imports da classe

class Relay:
    def __init__(self, pin):
        self.relay = Pin(pin, Pin.OUT)
        self.state = State(0)
        self.relay.value(self.state.value)

    def on(self):
        self.state.on()
        self.relay.value(self.state.value)

    def off(self):
        self.state.off()
        self.relay.value(self.state.value)

    def toggle(self):
        self.state.toggle()
        self.relay.value(self.state.value)

#############################################################################################################################
#classe responsavel pelo gerenciamento de estrados de portas I/O on/off
#imports da classe
class State:
    def __init__(self, state):
        self.value = state

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0

    def toggle(self):
        self.value = 0 if self.value else 1
#############################################################################################################################
#classe responsavel pelo gerenciamento do display oled ssd1306
#imports da classe
import ssd1306
import framebuf
import time

class OledManager:
    def __init__(self, scl=22, sda=21, width=128, height=64):
        i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda))
        self.oled = ssd1306.SSD1306_I2C(width, height, i2c)
        self.width = width
        self.height = height

    def limpar(self):
        self.oled.fill(0)
        self.oled.show()

    def display_texto(self, mensagens):
        """
        Mostra uma lista de mensagens na tela
        Divide automaticamente na tela
        """
        self.oled.fill(0)
        linhas = len(mensagens)

        if linhas == 0:
            return

        espacamento = int(self.height / linhas) if linhas > 3 else 20

        coluna = 0
        linha = 0

        for texto in mensagens:
            self.oled.text(str(texto), coluna, linha)
            linha += espacamento

        self.oled.show()

    def mostrar_mensagem(self, linha1, linha2="", linha3="", linha4=""):
        self.display_texto([linha1, linha2, linha3, linha4])

    def load_image(self, path):
        """
        Carrega uma imagem no formato PBM (ou RAW binário) do arquivo
        """
        with open(path, 'rb') as img:
            img.readline()  # P4 (PBM binário)
            img.readline()  # Comentário ou metadados
            img.readline()  # Dimensão da imagem
            data = bytearray(img.read())
            return data

    def mostrar_imagem(self, path_img, w, h, x=0, y=0, tempo=None):
        """
        Mostra uma imagem carregada do arquivo no display
        """
        data = self.load_image(path_img)
        buffer = framebuf.FrameBuffer(data, w, h, framebuf.MONO_HLSB)
        self.oled.blit(buffer, x, y)
        self.oled.show()
        if tempo:
            time.sleep(tempo)
            self.limpar()

    def invert(self, state=True):
        """
        Inverte as cores do OLED
        """
        self.oled.invert(1 if state else 0)

    def atualizar(self):
        self.oled.show()
