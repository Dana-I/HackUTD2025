from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit
import math
import json, wifiCfg, urequests

wifiCfg.doConnect("iPhone", "Jazz5465")

API_BASE = "http://10.169.166.159:8000"

setScreenColor(0x000000)
env3_0 = unit.get(unit.ENV3, unit.PORTA)

# Sound sensor via Grove Hub (connected to Port B, analog channel)
from machine import ADC, Pin
sound_sensor = ADC(Pin(36))  # Port B / Grove Hub slot 1 = GPIO36
sound_sensor.atten(ADC.ATTN_11DB)  # full range (0–3.3V)
sound_sensor.width(ADC.WIDTH_12BIT)  # 12-bit resolution (0–4095)

# Labels for data collection
title0 = M5Title(title="UNIT ENV III", x=120, fgcolor=0xFFFFFF, bgcolor=0xff0000)
statusLabel = M5TextBox(10, 50, "Status : ", lcd.FONT_DejaVu24, 0xffffff, rotate=0)
statusUpdate = M5TextBox(120, 50, " ", lcd.FONT_DejaVu24, 0x8B0000, rotate=0)

tempLabel = M5TextBox(30, 100, "Temperature (F) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
pressureLabel = M5TextBox(30, 130, "Pressure (hPa) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
humidityLabel = M5TextBox(30, 160, "Humidity (%) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
soundLabel = M5TextBox(30, 190, "Sound (db) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)

tempData = M5TextBox(210, 100, "Text", lcd.FONT_Default, 0xffffff, rotate=0)
pressureData = M5TextBox(210, 130, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
humidityData = M5TextBox(210, 160, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
soundData = M5TextBox(210, 190, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)

# variables
json_input = ""
steps = []
step_index = 0
show_stats = True
show_task = False

# Helper Function for Sound
def read_sound_level():
    total = 0
    samples = 50
    for i in range(samples):
        total += sound_sensor.read()
    avg = total / samples
    # Convert to approximate "dB" scale (not calibrated, just visual)
    db = (avg / 4095) * 100
    return round(db, 1)

# Infinite loop for live data
while True:
    if show_stats:
        tempC = env3_0.temperature
        tempF = tempC * 9 / 5 + 32
        pressure = env3_0.pressure
        humidity = env3_0.humidity
        
        # update data text boxes
        tempData.setText(str(tempF))
        pressureData.setText(str(pressure))
        humidityData.setText(str(humidity))
        decibel = read_sound_level()
        soundData.setText(str(decibel))

        # warning if temperature exceeds acceptable limit
        if tempF > 80:
            statusUpdate.setText("Temp too high!")
            rgb.setColorAll(0xff0000)
            statusUpdate.setColor(0x8B0000)
            title0.setBgColor(0xff0000)
        else:
            statusUpdate.setText("Normal stats")
            statusUpdate.setColor(0xffffff)
            rgb.setColorAll(0x00FF00)
            title0.setBgColor(0x00FF00)
            
        # send & get data from streamlit
        try:
            payload = {"temperature": tempF, "sound": sound}
            response = urequests.post(API_BASE + "/sensor_data", json=payload)
            if response.status_code == 200:
                json_input = response.text
                data = json.loads(json_input)
                steps = data.get("steps", [])
                if steps:
                    show_stats = False
                    show_task = True
                    tempLabel.setText("")
                    pressureLabel.setText("")
                    humidityLabel.setText("")
                    soundLabel.setText("")
                    tempData.setText("")
                    pressureData.setText("")
                    humidityData.setText("")
                    soundData.setText("")
                    lcd.clear()
            response.close()
        except Exception as e:
            statusUpdate.setText("Net Err")
            statusUpdate.setColor(0xFFFF00)

    elif show_task:
        if step_index < len(steps):
            lcd.print(steps[step_index], 10, 170, 0xFFFFFF)
            if btnB.isPressed():
                step_index += 1
                lcd.clear()
        else:
            show_task = False
            show_stats = True
            step_index = 0
            lcd.clear()





