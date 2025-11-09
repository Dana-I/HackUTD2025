from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types
import os, json
from dotenv import load_dotenv
from datetime import datetime

# Load .env file
load_dotenv()

# Initialize client (reads GEMINI_API_KEY from environment)
client = genai.Client()

# Create FastAPI app
app = FastAPI()

# Allow frontend (Streamlit / Pi)
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
        # New SDK uses client.models.generate_content()
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # change to gemini-2.5-flash if listed for your key
            contents=[prompt],
        )

        text = response.text.strip()

        # Remove Markdown code fences if Gemini adds them
        if text.startswith("```"):
            text = text.strip("`")  # remove backticks
            text = text.replace("json", "").replace("JSON", "").strip()

        # Try to extract the JSON array cleanly
        try:
            steps = json.loads(text)
        except Exception:
            # If still not valid JSON, fall back to splitting lines
            lines = [line.strip(" ,") for line in text.split("\n") if line.strip()]
            # Remove stray brackets or quotes
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

    # Check Fahrenheit thresholds
    alerts = []
    if temperature_f and temperature_f > 90:
        alerts.append(f"High Temperature Alert: {temperature_f}°F at {timestamp}")
    if sound and sound > 75:
        alerts.append(f"High Sound Alert: {sound}dB at {timestamp}")

    for alert in alerts:
        technician_log.append({
            "time": timestamp,
            "event": alert
        })

    return {"status": "ok", "alerts": alerts}

@app.post("/update_status")
async def update_status(request: Request):
    data = await request.json()
    step = data.get("step")
    action = data.get("action")
    timestamp = datetime.now().strftime("%H:%M:%S")
    technician_log.append({"time": timestamp, "event": f"Step '{step}' marked as {action}"})
    return {"status": "logged"}


@app.get("/logs")
def get_logs():
    return {"logs": technician_log}


@app.get("/sensor_logs")
def get_sensor_logs():
    return {"data": sensor_data_log[-50:]}  # last 50 readings for graph