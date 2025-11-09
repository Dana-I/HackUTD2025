# usb_reader.py - Run this on your computer
import serial
import json
import requests
import time
from datetime import datetime

# Backend URL (now using localhost since everything runs on same machine)
API_BASE = "http://localhost:8000"

# Find your M5Go's serial port
# On Mac: /dev/cu.usbserial-* or /dev/ttyUSB*
# On Windows: COM3, COM4, etc.
SERIAL_PORT = "/dev/cu.usbserial-58FE0073171"  #  actual port

def find_m5go_port():
    """Try to automatically find the M5Go serial port"""
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Found: {port.device} - {port.description}")
        if "USB" in port.description or "Serial" in port.description:
            return port.device
    return None

def main():
    port = find_m5go_port()
    if not port:
        print("M5Go not found. Please check USB connection.")
        return
    
    print(f"Connecting to M5Go on {port}...")
    
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        print("Connected to M5Go!")
        
        while True:
            try:
                # Read line from M5Go
                line = ser.readline().decode('utf-8').strip()
                
                if line and line.startswith('{'):
                    # Parse JSON data
                    sensor_data = json.loads(line)
                    print(f"Received: {sensor_data}")
                    
                    # Send to FastAPI backend
                    try:
                        response = requests.post(
                            f"{API_BASE}/sensor_log",
                            json=sensor_data,
                            timeout=2
                        )
                        if response.status_code == 200:
                            print("✓ Data sent to backend")
                        else:
                            print(f"✗ Backend error: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        print(f"✗ Cannot reach backend: {e}")
                
            except json.JSONDecodeError:
                print(f"Invalid JSON: {line}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                
            time.sleep(0.1)
                
    except serial.SerialException as e:
        print(f"Serial connection failed: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
        print("Disconnected")

if __name__ == "__main__":
    main()