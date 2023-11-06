import network
import utime as time
import machine
import datetime #You must import the library
import rp2
import sys
import usocket as socket
import ustruct as struct
import config

from machine import RTC
from time import sleep
from umqtt.simple import MQTTClient
from machine import Pin
 
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(config.SSID, config.PASSWORD)

# Start temperature reader configuration
sensor_temp = machine.ADC(4)
conversion_factor = 3.3 / (65535)
# Temperature difference between RBPI Pico and environment
dif_sensor_temp = 5

# Winter / Summer
GMT_OFFSET = 3600 * 1 # 3600 = 1 h (Winter)
#GMT_OFFSET = 3600 * 2 # 3600 = 1 h (Summer)

# NTP-Host
NTP_HOST = 'pool.ntp.org'

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

def read_temperature():
    reading = sensor_temp.read_u16() * conversion_factor 
    temperature = 27 - (reading - 0.706)/0.001721
    topic_msg = b'{"buttonpressed":"1", "temperature":"1"}'
    #print(round(temperature, 1))
    return temperature - dif_sensor_temp

# Function: get time from NTP Server
def getTimeNTP():
    NTP_DELTA = 2208988800
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    ntp_time = struct.unpack("!I", msg[40:44])[0]
    return time.gmtime(ntp_time - NTP_DELTA + GMT_OFFSET)

# Function: copy time to PI pico´s RTC
def setTimeRTC():
    tm = getTimeNTP()
    rtc.datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

def get_datetime_rtc():
    dt = rtc.datetime()
    d = datetime.datetime(dt[0], dt[1], dt[2], dt[4], dt[5], dt[6], dt[7])
    return d

def get_topic_msg():
    return b'{"buttonpressed":"' + str (button.value()) + '", "temperature":"' + str (read_temperature()) + '", "datetime":"' + str (get_datetime_rtc()) +'"}'


rtc = RTC()
setTimeRTC()
print(rtc.datetime())
lastMinute = rtc.datetime()[5]

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
        if lastMinute < rtc.datetime()[5]:
            lastMinute = rtc.datetime()[5]
            client.publish(config.topic_pub, get_topic_msg())
        if button.value():
            client.publish(config.topic_pub, get_topic_msg())
            time.sleep(0.5)
            #print(get_topic_msg())
            #print(rtc.datetime())
        else:
            pass
        

        
    except Exception as e:
        print(e)
        reconnect()
