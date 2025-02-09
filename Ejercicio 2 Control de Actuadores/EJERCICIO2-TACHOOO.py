from machine import Pin, time_pulse_us
import network
import time
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "Ubee9779-2.4G"
WIFI_PASSWORD = "A266879779"

# Configuración MQTT
MQTT_BROKER = "192.168.0.24"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "esp32_ultrasonico"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "jla/ejercicio"
MQTT_TOPIC_SUB = "led/control"

# Configuración del sensor ultrasónico
TRIG_PIN = 15
ECHO_PIN = 4

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

# Configuración del LED RGB
LED_R = Pin(27, Pin.OUT)
LED_G = Pin(25, Pin.OUT)
LED_B = Pin(26, Pin.OUT)

LED_R.value(0)
LED_G.value(0)
LED_B.value(0)

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    # Intentar conectar por 10 segundos
    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\nError al conectar a WiFi: Tiempo de espera agotado")
            return False
        print(".", end="")
        time.sleep(0.3)
    
    print("\nWiFi Conectada!")
    return True

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC_PUB}, Suscrito a: {MQTT_TOPIC_SUB}")
    return client

# Función para medir distancia con HC-SR04
def medir_distancia():
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

    duracion = time_pulse_us(echo, 1, 30000)  # Máximo 30 ms de espera
    if duracion < 0:
        return -1  # Error en la medición
    
    distancia = (duracion * 0.0343) / 2  # Convertir a cm
    return distancia

# Función para controlar el LED RGB según la distancia
import time
def actualizar_led(distancia):
    if 1 <= distancia <= 10:
        LED_R.value(0)
        LED_G.value(1)
        LED_B.value(0)
        color = "rojo"
    elif 10 <= distancia <= 30:
        LED_R.value(1)
        LED_G.value(1)
        LED_B.value(0)
        color = "amarillo"
    else:
        LED_R.value(1)
        LED_G.value(0)
        LED_B.value(0)
        color = "verde"
    
    time.sleep(0.1)  # Pequeña pausa para estabilizar el color
    return color


# Conectar a WiFi y MQTT
conectar_wifi()
client = conectar_broker()

distancia_anterior = -1  # Inicializamos con un valor inválido

# Bucle principal
while True:
    distancia = medir_distancia()
    print(f"Distancia: {distancia} cm")

    if distancia != distancia_anterior:
        color = actualizar_led(distancia)
        client.publish(MQTT_TOPIC_PUB, f"{distancia},{color}")
        distancia_anterior = distancia  # Actualizar la distancia anterior

    time.sleep(2)  # Esperar 2 segundos antes de la siguiente medición
