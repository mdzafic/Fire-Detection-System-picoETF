from ili934xnew import ILI9341, color565
from machine import Pin, SPI, ADC
from micropython import const
from umqtt.simple import MQTTClient
import glcdfont
import tt14
import tt24
import tt32
import time
import network

# --- WiFi Povezivanje ---
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Povezivanje na WiFi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print("Povezano:", wlan.ifconfig())

connect_wifi("DZAFIC", "29122004")

# --- MQTT Konfiguracija ---
TOPIC_TEMP = b"picoETF/temperatura"
TOPIC_STATUS = b"picoETF/status"
TOPIC_PUMPA = b"picoETF/pumpa"

manual_mode = False  # Automatski režim po defaultu

def sub_cb(topic, msg):
    global manual_mode
    if topic == TOPIC_PUMPA:
        if msg == b"auto":
            manual_mode = False # Automatski režim
        else:
            manual_mode = True # Ručni režim
            if msg == b"1":
                relay.value(0)  # Uključi pumpu
            elif msg == b"0":
                relay.value(1)  # Isključi pumpu

mqtt_client = MQTTClient("pico_plamen", "broker.hivemq.com")
mqtt_client.set_callback(sub_cb)
mqtt_client.connect()
mqtt_client.subscribe(TOPIC_PUMPA)

# --- HARDVER ---
adc = ADC(Pin(28))                 # LM35
do_flame = Pin(14, Pin.IN)         # Senzor za plamen
relay = Pin(13, Pin.OUT)           # Relej (pumpa)
relay.value(1)                     # Isključeno na startu

# Displej konfiguracija
SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
SCR_ROT = const(2)

TFT_CLK_PIN = const(18)
TFT_MOSI_PIN = const(19)
TFT_MISO_PIN = const(16)
TFT_CS_PIN = const(17)
TFT_RST_PIN = const(20)
TFT_DC_PIN = const(15)

spi = SPI(0,
          baudrate=62500000,
          miso=Pin(TFT_MISO_PIN),
          mosi=Pin(TFT_MOSI_PIN),
          sck=Pin(TFT_CLK_PIN))

display = ILI9341(spi,
                  cs=Pin(TFT_CS_PIN),
                  dc=Pin(TFT_DC_PIN),
                  rst=Pin(TFT_RST_PIN),
                  w=SCR_WIDTH,
                  h=SCR_HEIGHT,
                  r=SCR_ROT)

display.set_font(tt24)
display.rotation = 3

def nacrtaj_veliku_vatru(x0, y0):
    display.fill_rectangle(x0 + 10, y0 + 60, 60, 20, color565(255, 0, 0))       # crvena
    display.fill_rectangle(x0 + 20, y0 + 40, 40, 20, color565(255, 69, 0))      # narandžasta
    display.fill_rectangle(x0 + 30, y0 + 20, 20, 20, color565(255, 215, 0))     # žuta
    display.fill_rectangle(x0 + 38, y0 + 10, 4, 10, color565(255, 255, 0))      # vrh

# --- Glavna petlja ---
while True:
    # Čitanje temperature
    raw = adc.read_u16()
    temp_c = raw * 330 / 65535

    # Čitanje flame senzora (0 = detektovan plamen)
    flame_status = do_flame.value()

    # Slanje MQTT poruka
    mqtt_client.publish(TOPIC_TEMP, str(round(temp_c, 2)))
    mqtt_client.check_msg()

    # Čišćenje ekrana
    display.fill_rectangle(0, 0, display.width, display.height, color565(0, 0, 0))
    display.set_pos(10, 10)
    display.set_color(color565(255, 255, 255), color565(0, 0, 0))
    display.print(f"Temperatura: {round(temp_c, 2)} C")

    if flame_status == 0:
        display.set_pos(10, 40)
        display.set_color(color565(255, 0, 0), color565(0, 0, 0))
        display.print("PLAMEN DETEKTOVAN!")
        nacrtaj_veliku_vatru(60, 100)
        mqtt_client.publish(TOPIC_STATUS, b"PLAMEN DETEKTOVAN!")

        if not manual_mode:
            relay.value(0)  # Automatski uključi pumpu
    else:
        display.set_pos(10, 40)
        display.set_color(color565(255, 255, 255), color565(0, 0, 0))
        display.print("Nema plamena")
        mqtt_client.publish(TOPIC_STATUS, b"Nema plamena")

        if not manual_mode:
            relay.value(1)  # Automatski isključi pumpu

    time.sleep(2)

