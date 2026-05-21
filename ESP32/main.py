# main.py -- put your code here!import network
import socket
import time
import math
from machine import Pin, ADC
import network

# ---------------- CONFIG ----------------
WIFI_SSID = "username"
WIFI_PASS = "password"
PC_IP     = "192.168.1.202"   # your PC's local IP
PC_PORT   = 5005

# ---------------- HARDWARE ----------------
led = Pin(2, Pin.OUT)
button_pins = [13, 12, 14, 27, 26, 25, 33, 32]
buttons = [Pin(p, Pin.IN, Pin.PULL_UP) for p in button_pins]
last_states = [1] * len(buttons)

pot = ADC(Pin(34))
pot.atten(ADC.ATTN_11DB)
pot.width(ADC.WIDTH_12BIT)
POT_MIN, POT_MAX = 0, 4095
last_volume = -1

# ---------------- WIFI ----------------
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASS)
        for _ in range(20):          # 10s timeout
            if wlan.isconnected():
                break
            time.sleep(0.5)
    print("WiFi:", wlan.ifconfig())
    return wlan.isconnected()

# ---------------- VOLUME ----------------
def read_volume():
    readings = sorted(pot.read() for _ in range(20))
    trimmed = readings[3:-3]
    raw = sum(trimmed) // len(trimmed)
    raw = max(POT_MIN + 1, min(POT_MAX, raw))
    normalized = (raw - POT_MIN) / (POT_MAX - POT_MIN)
    corrected = math.log(1 + normalized * 9) / math.log(10)
    return max(0, min(100, int(corrected * 100)))

# ---------------- SEND ----------------
sock = None

def init_socket():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP

def send(msg):
    try:
        sock.sendto(msg.encode(), (PC_IP, PC_PORT))
        led.value(1)
        led.value(0)
    except Exception as e:
        print("Send error:", e)

# ---------------- MAIN ----------------
connect_wifi()
init_socket()
pending = []

while True:
    for i, btn in enumerate(buttons):
        current = btn.value()
        if current == 0 and last_states[i] == 1:
            print(f"BTN{i+1}")
            pending.append(f"BTN{i+1}")
        last_states[i] = current

    volume = read_volume()
    if abs(volume - last_volume) > 3:
        send(f"VOL:{volume}")
        last_volume = volume

    if pending:
        send(pending.pop(0))

    time.sleep_ms(20)