import _thread
from components import Lamp, LightSwitch1, DHT11Sensor, MQ2Sensor, OledManager
from web_server import WebServer
from mqtt_manager import MQTTManager
import time
from machine import Timer
import config

# Inicializa o OLED
oled = OledManager()

# Lâmpadas
lamp_cozinha = Lamp(4, 16)
lamp_quarto = Lamp(17, 5)
lamp_sala = Lamp(18, 19)

# Interruptores
switch_cozinha = LightSwitch1(13)
switch_quarto = LightSwitch1(12)
switch_sala = LightSwitch1(14)

# Sensor DHT11 no quarto
sensor_dht = DHT11Sensor(pin=15)

# Sensor de gás na cozinha
API_KEY = config.API_KEY
NUMERO = config.NUMERO

sensor_gas = MQ2Sensor(
    pin_adc=34,
    pin_digital=35,
    alerta_pin=2,
    api_key=API_KEY,
    numero=NUMERO
)

# Variáveis para armazenar últimos estados
last_status = {
    "cozinha": None,
    "sala": None,
    "quarto": None,
    "temperatura": None,
    "umidade": None,
    "gas_ppm": None,
    "gas_nivel": None,
    "gas_digital": None
}

# Função para publicação apenas quando houver mudança
def mqtt_publish_if_changed(topic, value, key):
    if last_status.get(key) != value:
        mqtt.publish(topic, value)
        print(f"[MQTT] Publicado {topic}: {value}")
        last_status[key] = value

# Thread para ouvir botões físicos
def ouvindoBtn():
    while True:
        switch_cozinha.pressBTN(lamp_cozinha.toggle)
        switch_quarto.pressBTN(lamp_quarto.toggle)
        switch_sala.pressBTN(lamp_sala.toggle)

_thread.start_new_thread(ouvindoBtn, ())

# Wi-Fi
SSID = config.WIFI_SSID
PASSWORD = config.WIFI_PASSWORD
server = WebServer()
server.connect_wifi(SSID, PASSWORD)

# MQTT
MQTT_BROKER = config.MQTT_BROKER
CLIENT_ID = config.MQTT_CLIENT_ID

def mqtt_callback(topic, msg):
    topic = topic.decode()
    msg = msg.decode()

    print('MQTT recebido:', topic, msg)

    if topic == 'quarto/lamp/cmd':
        lamp_quarto.on() if msg == 'on' else lamp_quarto.off()
        mqtt_publish_if_changed('quarto/status', 'on' if lamp_quarto.state.value else 'off', 'quarto')

    elif topic == 'sala/lamp/cmd':
        lamp_sala.on() if msg == 'on' else lamp_sala.off()
        mqtt_publish_if_changed('sala/status', 'on' if lamp_sala.state.value else 'off', 'sala')

    elif topic == 'cozinha/lamp/cmd':
        lamp_cozinha.on() if msg == 'on' else lamp_cozinha.off()
        mqtt_publish_if_changed('cozinha/status', 'on' if lamp_cozinha.state.value else 'off', 'cozinha')

mqtt = MQTTManager(
    client_id=CLIENT_ID,
    broker=MQTT_BROKER,
    callback=mqtt_callback
)

mqtt.connect()
mqtt.subscribe('cozinha/lamp/cmd')
mqtt.subscribe('quarto/lamp/cmd')
mqtt.subscribe('sala/lamp/cmd')

# Tela de inicialização no OLED
oled.limpar()
oled.mostrar_imagem('logo.pbm', w=64, h=64, x=32, y=0, tempo=3)
oled.display_texto(["Automação ON", "Wi-Fi OK", "MQTT OK"])

# Loop principal
try:
    while True:
        dht = sensor_dht.ler()
        gas = sensor_gas.verificar_alerta()

        # Atualiza display OLED
        oled.display_texto([
            f"Temp: {dht['temperatura']}C",
            f"Umid: {dht['umidade']}%",
            f"Gas: {gas['ppm']}ppm",
            f"Nivel: {gas['nivel']}"
        ])

        # Publica estados das lâmpadas
        mqtt_publish_if_changed('cozinha/status', 'on' if lamp_cozinha.state.value else 'off', 'cozinha')
        mqtt_publish_if_changed('sala/status', 'on' if lamp_sala.state.value else 'off', 'sala')
        mqtt_publish_if_changed('quarto/status', 'on' if lamp_quarto.state.value else 'off', 'quarto')

        # Publica sensores
        mqtt_publish_if_changed('quarto/temperatura', dht['temperatura'], 'temperatura')
        mqtt_publish_if_changed('quarto/umidade', dht['umidade'], 'umidade')
        mqtt_publish_if_changed('cozinha/gas', gas['ppm'], 'gas_ppm')
        mqtt_publish_if_changed('cozinha/gas/nivel', gas['nivel'], 'gas_nivel')
        mqtt_publish_if_changed('cozinha/gas/digital', gas['alerta_whatsapp'], 'gas_digital')

        mqtt.check_msg()
        time.sleep(1)

finally:
    mqtt.disconnect()
    server.close()
