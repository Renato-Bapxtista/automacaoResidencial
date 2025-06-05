import _thread
from components import Lamp, LightSwitch2, DHT11Sensor, MQ2Sensor, OledManager
from web_server import WebServer
from mqtt_manager import MQTTManager
import time
from machine import RTC, Timer
import config

#Inicializa o OLED
oled = OledManager()

#Lâmpadas
lamp_cozinha = Lamp(4, 16)
lamp_quarto = Lamp(17, 5)
lamp_sala = Lamp(18, 19)

#Interruptores
switch_cozinha = LightSwitch2(13)
switch_quarto = LightSwitch2(12)
switch_sala = LightSwitch2(14)

#Sensor DHT11 no quarto
sensor_dht = DHT11Sensor(pin=15)

#Sensor de gás na cozinha
API_KEY = config.API_KEY
NUMERO = config.NUMERO

sensor_gas = MQ2Sensor(
    pin_adc=34,
    pin_digital=35,
    alerta_pin=2,
    api_key=API_KEY,
    numero=NUMERO
)

#Thread para botões físicos
def ouvindoBtn():
    while True:
        switch_cozinha.pressBTN(lamp_cozinha.toggle)
        switch_quarto.pressBTN(lamp_quarto.toggle)
        switch_sala.pressBTN(lamp_sala.toggle)

_thread.start_new_thread(ouvindoBtn, ())

#Wi-Fi
SSID = config.WIFI_SSID
PASSWORD = config.WIFI_PASSWORD
server = WebServer()
server.connect_wifi(SSID, PASSWORD)

#MQTT
MQTT_BROKER = config.MQTT_BROKER
CLIENT_ID = config.MQTT_CLIENT_ID

def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()

    print('MQTT recebido:', topic, msg)

    if topic == 'quarto/lamp/cmd':
        lamp_quarto.on() if msg == 'on' else lamp_quarto.off()
        mqtt.publish('quarto/status', 'on' if lamp_quarto.state.value else 'off')

    elif topic == 'sala/lamp/cmd':
        lamp_sala.on() if msg == 'on' else lamp_sala.off()
        mqtt.publish('sala/status', 'on' if lamp_sala.state.value else 'off')

    elif topic == 'cozinha/lamp/cmd':
        lamp_cozinha.on() if msg == 'on' else lamp_cozinha.off()
        mqtt.publish('cozinha/status', 'on' if lamp_cozinha.state.value else 'off')

mqtt = MQTTManager(
    client_id=CLIENT_ID,
    broker=MQTT_BROKER,
    callback=mqtt_callback
)

mqtt.connect()
mqtt.subscribe('cozinha/lamp/cmd')
mqtt.subscribe('quarto/lamp/cmd')
mqtt.subscribe('sala/lamp/cmd')

#Tela de inicialização
oled.limpar()
oled.mostrar_imagem('logo.pbm', w=64, h=64, x=32, y=0, tempo=3)
oled.display_texto(["Automação ON", "Wi-Fi OK", "MQTT OK"])

#função pra publicar no mqtt
def mqtt_pubolish():
    mqtt.publish('cozinha/status', 'on' if lamp_cozinha.state.value else 'off')
    mqtt.publish('quarto/status', 'on' if lamp_quarto.state.value else 'off')
    mqtt.publish('sala/status', 'on' if lamp_sala.state.value else 'off')

    mqtt.publish('quarto/temperatura', dht['temperatura'])
    mqtt.publish('quarto/umidade', dht['umidade'])

    mqtt.publish('cozinha/gas', gas['ppm'])
    mqtt.publish('cozinha/gas/nivel', gas['nivel'])
    mqtt.publish('cozinha/gas/digital', gas['alerta_whatsapp'])
    
timer_mqtt_publish = Timer(1)
timer_mqtt_publish.init(period=600000, mode=Timer.PERIODIC, callback=lambda t: mqtt_pubolish())

#estados das lampadas
lampada_cozinha = lamp_cozinha.state.value
lampada_sala = lamp_sala.state.value
lampada_quarto = lamp_quarto.state.value

mqtt_pubolish()
#Loop principal
try:
    while True:
        dht = sensor_dht.ler()
        gas = sensor_gas.verificar_alerta()
        
        oled.display_texto([
            f"Temp: {dht['temperatura']}C",
            f"Umid: {dht['umidade']}%",
            f"Gas: {gas['ppm']}ppm",
            f"Nivel: {gas['nivel']}"
        ])

        mqtt.check_msg()
        #mudança de estado das lampadas
        if lamp_cozinha.state.value != lampada_cozinha:
            lampada_cozinha = lamp_cozinha.state.value
            mqtt.publish('cozinha/status', 'on' if lamp_cozinha.state.value else 'off')
            
        if lamp_sala.state.value != lampada_sala:
            lampada_sala = lamp_sala.state.value
            mqtt.publish('sala/status', 'on' if lamp_sala.state.value else 'off')
        
        if lamp_quarto.state.value != lampada_quarto:
            lampada_quarto = lamp_quarto.state.value
            mqtt.publish('quarto/status', 'on' if lamp_quarto.state.value else 'off')
            
        if gas['alerta_whatsapp'] == 'on':
            mqtt.publish('cozinha/gas/digital', gas['alerta_whatsapp'])

        time.sleep(1)

finally:
    mqtt.disconnect()
    server.close()
