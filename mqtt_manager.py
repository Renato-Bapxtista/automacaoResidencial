# mqtt_manager.py

from umqtt.simple import MQTTClient
import time

class MQTTManager:
    def __init__(self, client_id, broker, port=1883, user=None, password=None, callback=None):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.user = user
        self.password = password
        self.callback = callback

        self.client = MQTTClient(
            client_id=self.client_id,
            server=self.broker,
            port=self.port,
            user=self.user,
            password=self.password
        )

        if callback:
            self.client.set_callback(callback)

    def connect(self):
        try:
            self.client.connect()
            print('MQTT conectado ao broker:', self.broker)
        except Exception as e:
            print('Erro na conexão MQTT:', e)

    def subscribe(self, topic):
        self.client.subscribe(topic.encode())
        print(f'Subscrito no tópico: {topic}')

    def publish(self, topic, message):
        try:
            self.client.publish(topic.encode(), str(message))
            print(f'Publicado -> {topic}: {message}')
        except Exception as e:
            print(f'Erro ao publicar em {topic}:', e)

    def check_msg(self):
        try:
            self.client.check_msg()
        except Exception as e:
            print('Erro no check_msg MQTT:', e)

    def disconnect(self):
        self.client.disconnect()
        print('MQTT desconectado')
