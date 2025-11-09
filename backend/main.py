from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import os, json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# reads GEMINI_API_KEY from env
client = genai.Client()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Gemini (google-genai 1.47.0) backend is running!"}

@app.post("/generate_steps")
async def generate_steps(request: Request):
    body = await request.json()
    description = body["description"]

    prompt = (
        "You are a data center assistant. "
        "Given a maintenance ticket description, break it into 5–7 clear, safety-aware steps. "
        "Output as a JSON array of strings only.\n\n"
        f"Task: {description}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=[prompt],
        )

        text = response.text.strip()

        # Parse through JSON response
        if text.startswith("```"):
            text = text.strip("`")  
            text = text.replace("json", "").replace("JSON", "").strip()

        try:
            steps = json.loads(text)
        except Exception:
            lines = [line.strip(" ,") for line in text.split("\n") if line.strip()]
            steps = [
                l.strip('"').strip(",").strip()
                for l in lines
                if not l.startswith("[") and not l.startswith("]") and not l.startswith("{")
            ]

        return {"steps": steps}

    except Exception as e:
        return {"error": str(e)}
    
sensor_data_log = []
technician_log = []

LOG_FILE = "technician_log.txt"

def save_log(event: dict):
    technician_log.append(event)

    # Append to file so it persists
    with open(LOG_FILE, "a") as f:
        f.write(f"{event['timestamp']} — {event['event']}\n")


@app.post("/sensor_data")
async def sensor_data(request: Request):
    data = await request.json()
    temperature_f = data.get("temperature")  # Fahrenheit value from M5Go
    sound = data.get("sound")
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Log readings
    sensor_data_log.append({
        "time": timestamp,
        "temperature": temperature_f,
        "sound": sound
    })

    # Check Fahrenheit and sound thresholds
    alerts = []
    if temperature_f and temperature_f > 90:
        alerts.append(f"High Temperature Alert: {temperature_f}°F at {timestamp}")
    if sound and sound > 85:
        alerts.append(f"High Sound Alert: {sound}dB at {timestamp}")

    # Sustained noise warning (>= 75 dB for ~5 readings in a row)
    recent_sound_readings = [
        entry["sound"] for entry in sensor_data_log[-5:]
        if entry.get("sound") is not None
    ]

    if len(recent_sound_readings) == 5 and all(value >= 75 for value in recent_sound_readings):
        save_log({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": "Sustained High Noise (≥ 75 dB for ~10–15s)"
        })
        
    for alert in alerts:
        save_log({
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "event": alert
        })

    return {"status": "ok", "alerts": alerts}

@app.post("/update_status")
async def update_status(request: Request):
    data = await request.json()
    step = data.get("step")
    action = data.get("action")
    timestamp = datetime.now().strftime("%H:%M:%S")
    save_log({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": f"Step '{step}' marked as {action}"
    })
    return {"status": "logged"}


@app.get("/logs")
def get_logs():
    return {"logs": technician_log}

@app.get("/log_file")
def get_log_file():
    try:
        with open(LOG_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

@app.get("/sensor_logs")
def get_sensor_logs():
    return {"data": sensor_data_log[-50:]}  # last 50 readings for graph

@app.get("/ping")
def ping():
    return {"status": "ok"}
