from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit


setScreenColor(0x000000)
env3_0 = unit.get(unit.ENV3, unit.PORTA)


random2 = None
i = None


label0 = M5TextBox(30, 104, "Temperature (F) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label1 = M5TextBox(30, 144, "Pressure (hPa) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label2 = M5TextBox(30, 185, "Humidity (%) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label8 = M5TextBox(30, 220, "Sound (db) :", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label3 = M5TextBox(210, 104, "Text", lcd.FONT_Default, 0xffffff, rotate=0)
title0 = M5Title(title="UNIT ENV III", x=120, fgcolor=0xFFFFFF, bgcolor=0xff0000)
label4 = M5TextBox(210, 144, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label5 = M5TextBox(210, 184, "Text", lcd.FONT_Default, 0xFFFFFF, rotate=0)
label6 = M5TextBox(20, 50, "Status : ", lcd.FONT_DejaVu24, 0xffffff, rotate=0)
label7 = M5TextBox(60, 50, " ", lcd.FONT_DejaVu24, 0x8B0000, rotate=0)


while True:
  tempC = env3_0.temperature
  tempF = tempC * 9 / 5 + 32
  label3.setText(str(tempF))
  label4.setText(str(env3_0.pressure))
  label5.setText(str(env3_0.humidity))
  
  if (tempF > 72):
    label7.setText("Temp too high!")
    label7.setColor(0x8B0000)
  else
    label17.setText("Temp OK")
    label7.setColor(0xffffff)
    
  mic_value = adc.read()  # Get analog sound level
  db = 20 * math.log10(mic_value / reference_value)
  
  wait(0.1)
  wait_ms(2)
  
  
