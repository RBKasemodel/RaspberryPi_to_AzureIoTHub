import network
import time
import machine
import config

from umqtt.simple import MQTTClient
from machine import Pin
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PASSWORD)
 
# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
 
led = Pin(15, Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

def mqtt_connect():

    certificate_path = "digicert.cer"
    print('Loading Digicert Certificate')
    with open(certificate_path, 'r') as f:
        cert = f.read()
    print('Obtained Digicert Certificate')
    sslparams = {'cert':cert}
    
    client = MQTTClient(client_id=config.clientid, server=config.hostname, port=config.port_no, user=config.user_name, password=config.passw, keepalive=3600, ssl=True, ssl_params=sslparams)
    client.connect()
    print('Connected to IoT Hub MQTT Broker')
    return client

def reconnect():
    print('Failed to connect to the MQTT Broker. Reconnecting...')
    time.sleep(5)
    machine.reset()

def callback_handler(topic, message_receive):
    print("Received message")
    print(message_receive)
    if message_receive.strip() == b'led_on':
        led.value(1)
        #print("led Turn ON")
    else:
        led.value(0)
        #print("led Turn OFF")

try:
    client = mqtt_connect()
    client.set_callback(callback_handler)
    client.subscribe(topic=config.subscribe_topic)
except OSError as e:
    reconnect()

while True:
    
    try:
        client.check_msg()
        time.sleep(0.5)
        if button.value():
            client.publish(config.topic_pub, config.topic_msg)
            time.sleep(0.5)
        else:
            pass
    except Exception as e:
        print(e)
        reconnect()