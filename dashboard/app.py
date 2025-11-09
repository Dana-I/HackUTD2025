import streamlit as st
import requests
import pandas as pd
import time
from PIL import Image

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Data Center Technician Dashboard", layout="wide")
st.title("Data Center Assistant Dashboard")

st.subheader("Assign a New Ticket")
ticket_description = st.text_area("Enter ticket/task description:")

if st.button("Generate Actionable Steps (Gemini)"):
    with st.spinner("Generating steps..."):
        try:
            response = requests.post(f"{API_BASE}/generate_steps", json={"description": ticket_description})
            data = response.json()
            steps = data.get("steps", [])
            if steps:
                st.session_state["steps"] = steps
                st.success("Steps generated successfully!")
            else:
                st.error("No steps returned. Try again.")
        except Exception as e:
            st.error(f"Error contacting backend: {e}")

if "steps" in st.session_state:
    st.subheader("Actionable Steps")

    if "step_sent" not in st.session_state:
        st.session_state["step_sent"] = {i: False for i in range(len(st.session_state["steps"]))}

    for i, step in enumerate(st.session_state["steps"]):
        key = f"step_{i}"
        checked = st.checkbox(step, key=key)

        if checked and not st.session_state["step_sent"].get(i, False):
            try:
                requests.post(f"{API_BASE}/update_status",
                              json={"step": step, "action": "completed"}, timeout=3)
                st.session_state["step_sent"][i] = True
            except Exception:
                st.warning("Could not reach backend to log this step.")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Temperature Over Time (°F)")
    temp_chart = st.empty()
with col2:
    st.subheader("Sound Levels (dB)")
    sound_chart = st.empty()

st.subheader("Technician & Alert Log")
log_box = st.empty()

# Download log file button
if st.button("Download Full Log File"):
    try:
        log_file = requests.get(f"{API_BASE}/log_file").text
        st.download_button(
            label="Click to Download Log File",
            data=log_file,
            file_name="technician_log.txt",
            mime="text/plain"
        )
    except:
        st.error("Could not download logs. Backend not responding.")

df = pd.DataFrame(columns=["time", "temperature", "sound"])

while True:
    try:
        # Fetch sensor data from backend
        sensor_resp = requests.get(f"{API_BASE}/sensor_logs").json()
        sensors = sensor_resp.get("data", [])

        if sensors:
            df = pd.DataFrame(sensors)
            temp_chart.line_chart(df, x="time", y="temperature")
            sound_chart.line_chart(df, x="time", y="sound")

        log_resp = requests.get(f"{API_BASE}/logs").json()
        logs = log_resp.get("logs", [])
        full_log_text = "\n".join([f"{l['timestamp']} — {l['event']}" for l in logs])
        log_box.text(full_log_text)

        
        header_image = Image.open("assets/RavenHeader.png")
        st.image(header_image, use_container_width=True)

        time.sleep(3)

    except Exception as e:
        st.warning(f"Waiting for backend... {e}")
        time.sleep(3)
