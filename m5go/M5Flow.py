from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit
import math
import json, wifiCfg, urequests

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
json_input = {
    "description": "Replace faulty cooling fan in Rack C3",
    "steps": [
        "1. Safety First: Power down the affected rack (C3) and confirm power isolation. Verify using a multimeter.",
        "2. PPE Check: Put on appropriate Personal Protective Equipment (PPE), including safety glasses and antistatic wrist strap.",
        "3. Identify Faulty Fan: Locate and visually inspect the faulty cooling fan within Rack C3. Note its model number and location.",
        "4. Remove Faulty Fan: Carefully disconnect the power cable and any mounting hardware securing the faulty fan. Remove the fan.",
        "5. Install Replacement Fan: Install the new cooling fan, ensuring it is the correct model. Secure it with the appropriate mounting hardware and reconnect the power cable.",
        "6. Verify Operation: Power on Rack C3 and confirm the new fan is operating correctly and airflow is restored. Monitor temperature readings.",
        "7. Dispose of Faulty Fan: Properly dispose of the faulty fan according to data center e-waste procedures."
    ]
}
description = json_input["description"]
steps = json_input["steps"]
jsonLabel = M5TextBox(10, 100, "", lcd.FONT_DejaVu24, 0x000000, rotate=0)
stepLabel = M5TextBox(30, 100, "", lcd.FONT_Default, 0xFFFFFF, rotate=0)
step_index = 0
show_stats = True
show_task = False

noise_threshold = 85
noise_start_time = None
noise_warning_active = False

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
    
def wrap_text(text, max_chars=25):
    lines = []
    while len(text) > max_chars:
        split_at = text.rfind(" ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        lines.append(text[:split_at])
        text = text[split_at:].lstrip()
    lines.append(text)
    return lines

# Infinite loop for live data
while True:
    if show_stats:
        current_time = time.ticks_ms()
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
        
        if decibel > noise_threshold:
          if noise_start_time is None:
            noise_start_time = current_time
          elif time.ticks_diff(current_time, noise_start_time) > 5000:  # >5 seconds
            noise_warning_active = True
          else:
            noise_start_time = None
            noise_warning_active = False

        # warning if temperature exceeds acceptable limit
        if tempF > 90 and noise_warning_active:
          statusUpdate.setText("TOO LOUD&HOT")
          rgb.setColorAll(0xff0000)
          statusUpdate.setColor(0x8B0000)
          title0.setBgColor(0xff0000)
        elif tempF > 90:
          statusUpdate.setText("TOO HOT")
          rgb.setColorAll(0xff0000)
          statusUpdate.setColor(0x8B0000)
          title0.setBgColor(0xff0000)
        elif decibel > noise_threshold:  # immediate short warning
          statusUpdate.setText("Noise rising...")
          statusUpdate.setColor(0xFFFF00)
          rgb.setColorAll(0xFFFF00)
          title0.setBgColor(0xFFFF00)
        else:
          statusUpdate.setText("Normal stats")
          statusUpdate.setColor(0xffffff)
          rgb.setColorAll(0x00FF00)
          title0.setBgColor(0x00FF00)
            
      
            
        # send & get data from streamlit
        # try:
        #     payload = {"temperature": tempF, "sound": sound}
        #     response = urequests.post(API_BASE + "/sensor_data", json=payload)
        #     if response.status_code == 200:
        #         json_input = response.text
        #         data = json.loads(json_input)
        #         steps = data.get("steps", [])
        #         if steps:
        #             show_stats = False
        #             show_task = True
        #             tempLabel.setText("")
        #             pressureLabel.setText("")
        #             humidityLabel.setText("")
        #             soundLabel.setText("")
        #             tempData.setText("")
        #             pressureData.setText("")
        #             humidityData.setText("")
        #             soundData.setText("")
        #             lcd.clear()
        #     response.close()
        # except Exception as e:
        #     statusUpdate.setText("")
        #     statusUpdate.setColor(0xFFFF00)
        
        if (btnC.wasPressed()): # get task
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
          setScreenColor(0xFFFF00)
          jsonLabel.setText(description)
          # wrapped = wrap_text(description)
          # y = 30
          # for line in wrapped:
          #   lcd.print(line, 10, y, 0x000000)
          #   y += 20
          navLabel = M5TextBox(30, 220, " Back       Next", lcd.FONT_DejaVu18, 0x000000, rotate=0)

    elif show_task:
        tempC = env3_0.temperature
        tempF = tempC * 9 / 5 + 32
        
        if tempF > 90:
            rgb.setColorAll(0xff0000)
            title0.setBgColor(0xff0000)
        else:
            rgb.setColorAll(0x00FF00)
            title0.setBgColor(0x00FF00)
        time.sleep_ms(100)
          
        if step_index < len(steps):
            if btnB.isPressed() and step_index<len(steps):
                lcd.clear()
                wrapped = wrap_text(steps[step_index])
                y = 30
                for line in wrapped:
                  lcd.print(line, 10, y, 0x000000)
                  y += 20
                step_index += 1
                navLabel = M5TextBox(30, 220, " Back       Next", lcd.FONT_DejaVu18, 0x000000, rotate=0)
                
            if btnA.isPressed() and step_index>0:
                lcd.clear()
                wrapped = wrap_text(steps[step_index])
                y = 30
                for line in wrapped:
                  lcd.print(line, 10, y, 0x000000)
                  y += 20
                step_index -= 1
                navLabel = M5TextBox(30, 220, "    Back           Next", lcd.FONT_DejaVu18, 0x000000, rotate=0)
              
        else:
            setScreenColor(0x000000)
            statusLabel = M5TextBox(10, 50, "Status : ", lcd.FONT_DejaVu24, 0xffffff, rotate=0)
            tempLabel.setText("Temperature (F) :")
            pressureLabel.setText("Pressure (hPa) :")
            humidityLabel.setText("Humidity (%) :")
            soundLabel.setText("Sound (db) :")
            show_task = False
            show_stats = True
            step_index = 0
            
