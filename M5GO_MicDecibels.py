from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit
import math
import json

setScreenColor(0x000000)

# ENV III on Port A (unchanged)
env3_0 = unit.get(unit.ENV3, unit.PORTA)

# Sound sensor via Grove Hub (connected to Port B, analog channel)
from machine import ADC, Pin
sound_sensor = ADC(Pin(36))  # Port B / Grove Hub slot 1 = GPIO36
sound_sensor.atten(ADC.ATTN_11DB)  # full range (0–3.3V)
sound_sensor.width(ADC.WIDTH_12BIT)  # 12-bit resolution (0–4095)

# --- UI Elements ---
title0 = M5Title(title="UNIT ENV III", x=120, fgcolor=0xFFFFFF, bgcolor=0xff0000)
statusLabel = M5TextBox(10, 50, "Status : ", lcd.FONT_DejaVu24, 0xffffff, rotate=0)
statusUpdate = M5TextBox(120, 50, " ", lcd.FONT_DejaVu24, 0x8B0000, rotate=0)

tempLabel = M5TextBox(30, 100, "Temperature (F):", lcd.FONT_Default, 0xFFFFFF, rotate=0)
pressureLabel = M5TextBox(30, 130, "Pressure (hPa):", lcd.FONT_Default, 0xFFFFFF, rotate=0)
humidityLabel = M5TextBox(30, 160, "Humidity (%):", lcd.FONT_Default, 0xFFFFFF, rotate=0)
soundLabel = M5TextBox(30, 190, "Sound (dB):", lcd.FONT_Default, 0xFFFFFF, rotate=0)

tempData = M5TextBox(210, 100, "", lcd.FONT_Default, 0xffffff, rotate=0)
pressureData = M5TextBox(210, 130, "", lcd.FONT_Default, 0xFFFFFF, rotate=0)
humidityData = M5TextBox(210, 160, "", lcd.FONT_Default, 0xFFFFFF, rotate=0)
soundData = M5TextBox(210, 190, "", lcd.FONT_Default, 0xFFFFFF, rotate=0)

# --- JSON input placeholder (unchanged) ---
json_input = '''
{
  "steps": [
    "1. Safety First: Power down the affected rack (C3) and confirm power isolation.",
    "2. PPE Check: Don appropriate PPE including safety glasses and antistatic wrist strap.",
    "3. Identify Faulty Fan: Locate and inspect the faulty cooling fan in Rack C3.",
    "4. Remove Faulty Fan: Disconnect power and remove mounting hardware.",
    "5. Install Replacement Fan: Secure new fan and reconnect power.",
    "6. Verify Operation: Power on and confirm airflow and temperature.",
    "7. Dispose of Faulty Fan: Follow e-waste procedures."
  ]
}
'''
data = json.loads(json_input)
steps = data["steps"]
step_index = 0

show_stats = True
show_task = False

# --- Helper Function for Sound ---
def read_sound_level():
    total = 0
    samples = 50
    for i in range(samples):
        total += sound_sensor.read()
    avg = total / samples
    # Convert to approximate "dB" scale (not calibrated, just visual)
    db = (avg / 4095) * 100
    return round(db, 1)

# --- Main Loop ---
while show_stats:
    tempC = env3_0.temperature
    tempF = tempC * 9 / 5 + 32
    tempData.setText(str(round(tempF, 1)))
    pressureData.setText(str(round(env3_0.pressure, 1)))
    humidityData.setText(str(round(env3_0.humidity, 1)))

    decibel = read_sound_level()
    soundData.setText(str(decibel))

    # Status handling (one warning active at a time)
    if decibel > 20:
        statusUpdate.setText("Too loud!")
        statusUpdate.setColor(0xFF0000)
        rgb.setColorAll(0xFF0000)
        title0.setBgColor(0xFF0000)
    elif tempF > 80:
        statusUpdate.setText("Temp too high!")
        statusUpdate.setColor(0xFF0000)
        rgb.setColorAll(0xFF0000)
        title0.setBgColor(0xFF0000)
    else:
        statusUpdate.setText("Normal stats")
        statusUpdate.setColor(0x00FF00)
        rgb.setColorAll(0x00FF00)
        title0.setBgColor(0x00FF00)

    wait(0.2)




