# from m5stack import *
# from m5ui import *
# from uiflow import *
# import time
# import unit
# import math
# import json, wifiCfg, urequests

# wifiCfg.doConnect("iPhone", "Jazz5465")

# API_BASE = "https://algebraically-gimlety-flo.ngrok-free.dev"

# setScreenColor(0x000000)
# env3_0 = unit.get(unit.ENV3, unit.PORTA)

# # Sound sensor via Grove Hub (connected to Port B, analog channel)
# from machine import ADC, Pin
# sound_sensor = ADC(Pin(36))  # Port B / Grove Hub slot 1 = GPIO36
# sound_sensor.atten(ADC.ATTN_11DB)  # full range (0–3.3V)
# sound_sensor.width(ADC.WIDTH_12BIT)  # 12-bit resolution (0–4095)

# title0 = M5Title(title="UNIT ENV III", x=120, fgcolor=0xFFFFFF, bgcolor=0xff0000)
# statusLabel = M5TextBox(10, 50, "Status : ", lcd.FONT_DejaVu24, 0xffffff, rotate=0)
# statusUpdate = M5TextBox(120, 50, " ", lcd.FONT_DejaVu24, 0x8B0000, rotate=0)

# tempLabel = M5TextBox(30, 100, "Temperature (F) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
# pressureLabel = M5TextBox(30, 130, "Pressure (hPa) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
# humidityLabel = M5TextBox(30, 160, "Humidity (%) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
# soundLabel = M5TextBox(30, 190, "Sound (db) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)

# tempData = M5TextBox(210, 100, "Text", lcd.FONT_Default, 0xffffff, rotate=0)
# pressureData = M5TextBox(210, 130, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
# humidityData = M5TextBox(210, 160, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
# soundData = M5TextBox(210, 190, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)

# json_input = ""
# steps = []
# step_index = 0
# show_stats = True
# show_task = False

# # Helper Function for Sound
# def read_sound_level():
#     total = 0
#     samples = 50
#     for i in range(samples):
#         total += sound_sensor.read()
#     avg = total / samples
#     # Convert to approximate "dB" scale (not calibrated, just visual)
#     db = (avg / 4095) * 100
#     return round(db, 1)

# while True:
#     if show_stats:
#         tempC = env3_0.temperature
#         tempF = tempC * 9 / 5 + 32
#         pressure = env3_0.pressure
#         humidity = env3_0.humidity

#         tempData.setText(str(tempF))
#         pressureData.setText(str(pressure))
#         humidityData.setText(str(humidity))
#         decibel = read_sound_level()
#         soundData.setText(str(decibel))

#         if tempF > 80:
#             statusUpdate.setText("Temp too high!")
#             rgb.setColorAll(0xff0000)
#             statusUpdate.setColor(0x8B0000)
#             title0.setBgColor(0xff0000)
#         else:
#             statusUpdate.setText("Normal stats")
#             statusUpdate.setColor(0xffffff)
#             rgb.setColorAll(0x00FF00)
#             title0.setBgColor(0x00FF00)

#         try:
#             payload = {"temperature": tempF, "sound": decibel}
#             response = urequests.post(API_BASE + "/sensor_data", json=payload)
#             response.close()
#         except Exception as e:
#             statusUpdate.setText("Net Err")
#             statusUpdate.setColor(0xFFFF00)

#     elif show_task:
#         if step_index < len(steps):
#             lcd.print(steps[step_index], 10, 170, 0xFFFFFF)
#             if btnB.isPressed():
#                 step_index += 1
#                 lcd.clear()
#         else:
#             show_task = False
#             show_stats = True
#             step_index = 0
#             lcd.clear()

# m5go.py - USB Serial Version
from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit
import math
import json

setScreenColor(0x000000)
env3_0 = unit.get(unit.ENV3, unit.PORTA)

# Sound sensor setup
from machine import ADC, Pin
sound_sensor = ADC(Pin(36))
sound_sensor.atten(ADC.ATTN_11DB)
sound_sensor.width(ADC.WIDTH_12BIT)
noise_ref = None
ema_rms = None

# Display elements
title0 = M5Title(title="USB SENSOR DATA", x=120, fgcolor=0xFFFFFF, bgcolor=0x0000ff)
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

# def read_sound_level():
#     total = 0
#     samples = 50
#     for i in range(samples):
#         total += sound_sensor.read()
#     avg = total / samples
#     db = (avg / 4095) * 100
#     return round(db, 1)

def read_sound_level():
    global noise_ref, ema_rms
    samples = 200  # more samples -> better RMS
    vals = []
    for _ in range(samples):
        vals.append(sound_sensor.read())

    mean = sum(vals) / samples            # remove DC bias
    acc = 0.0
    for v in vals:
        d = v - mean
        acc += d * d
    rms = math.sqrt(acc / samples)        # RMS of AC component

    # establish a quiet reference automatically on first runs
    if noise_ref is None:
        noise_ref = max(rms, 1.0)         # avoid divide-by-zero

    # smooth RMS to reduce jitter
    alpha = 0.2
    ema_rms = rms if ema_rms is None else (alpha * rms + (1 - alpha) * ema_rms)

    # convert to approximate dB relative to the learned baseline
    ratio = ema_rms / max(noise_ref, 1.0)
    db_est = 20 * math.log10(ratio) + 50  # assume quiet baseline ≈ 50 dB

    # clamp to a reasonable SPL-like range
    if db_est < 30:
        db_est = 30
    if db_est > 100:
        db_est = 100

    return round(db_est, 1)


def send_serial_data():
    tempC = env3_0.temperature
    tempF = tempC * 9 / 5 + 32
    pressure = env3_0.pressure
    humidity = env3_0.humidity
    decibel = read_sound_level()
    
    # Create JSON data
    sensor_data = {
        "temperature": tempF,
        "sound": decibel,
        "pressure": pressure,
        "humidity": humidity
    }
    
    # Send via USB serial
    print(json.dumps(sensor_data))
    
    return tempF, pressure, humidity, decibel

# Main loop
while True:
    tempF, pressure, humidity, decibel = send_serial_data()
    
    # Update display
    tempData.setText(str(round(tempF, 1)))
    pressureData.setText(str(round(pressure, 1)))
    humidityData.setText(str(round(humidity, 1)))
    soundData.setText(str(decibel))
    
    # Status alerts
    if tempF > 90 or decibel > 80:
        statusUpdate.setText("CRITICAL ALERT!")
        rgb.setColorAll(0xff0000)
        statusUpdate.setColor(0x8B0000)
        title0.setBgColor(0xff0000)
    else:
        statusUpdate.setText("Normal")
        statusUpdate.setColor(0xffffff)
        rgb.setColorAll(0x00FF00)
        title0.setBgColor(0x00FF00)
    
    wait(2)  # Send data every 2 seconds