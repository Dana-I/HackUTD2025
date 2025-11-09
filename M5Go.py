from m5stack import *
from m5ui import *
from uiflow import *
import time
import unit

setScreenColor(0x000000)
env3_0 = unit.get(unit.ENV3, unit.PORTA)


random2 = None
i = None



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


show_stats = True
show_task = False

#sample input
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

while show_stats:
  tempC = env3_0.temperature
  tempF = tempC * 9 / 5 + 32
  tempData.setText(str(tempF))
  pressureData.setText(str(env3_0.pressure))
  humidityData.setText(str(env3_0.humidity))
  
  if (tempF > 80):
    statusUpdate.setText("Temp too high!")
    rgb.setColorAll(0xff0000)
    statusUpdate.setColor(0x8B0000)
    title0.setBgColor(0xff0000)
  else:
    statusUpdate.setText("Normal stats")
    statusUpdate.setColor(0xffffff)
    rgb.setColorAll(0x00FF00)
    title0.setBgColor(0x00FF00)
    
  wait(0.1)
  wait_ms(2)
    
while show_task:
  tempLabel.setText("")
  pressureLabel.setText("")
  humidityLabel.setText("")
  soundLabel.setText("")
  
  
 
  




  
  
