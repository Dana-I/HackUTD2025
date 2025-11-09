# Raven — Data Center Technician Assistant
HackUTD 2025 Project

Raven is a wearable assistant designed for data center technicians working in environments that are loud, hot, and constantly changing. Technicians often must navigate complex maintenance procedures while staying aware of environmental hazards (heat, sound, airflow, etc.). Raven combines real-time hardware sensing with AI-powered task assistance to help technicians stay safe, focused, and efficient.

### Hardware (Wearable Device)
- M5GO IoT device (ESP32-based)
- Built-in environmental sensors for temperature, humidity, pressure
- External sound sensor (ADC input for decibel estimation)
- UIFlow + MicroPython to stream sensor data over USB Serial

### Backend (Alerting + AI)
- FastAPI backend receives real-time data from M5GO
- Applies safety thresholds (ex: > 90°F or > 85 dB triggers alerts)
- Logs events persistently to a text file for audit history
- Gemini 2.0 Flash API generates step-by-step action plans

### Dashboard (Technician Console)
- Streamlit web app
- Plots live sensor data
- Displays logs of alerts and completed steps
- Allows downloading historical log files

## Setup and Run
Clone the repo and create a virtual environment:
```bash
git clone <repo>
cd HackUTD2025
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

To run programs:
1. Start FastAPI (uvicorn app:app --reload)
2. Start USB reader (python3 usb_reader.py)
3. Start Streamlit dashboard (streamlit run app.py)

To run file on M5Go through UIFlow interface
1. Go to https://flow.m5stack.com/
2. Connect M5Go to wifi network
3. Add API key of device to m5stack settings
4. Run file
