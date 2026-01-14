import psutil
import serial
import json
import time
import datetime
import sys

COM_PORT = "COM6"
BAUD_RATE = 115200
UPDATE_INTERVAL = 1.0

try:
    ser = serial.Serial(
        port=COM_PORT,
        baudrate=BAUD_RATE,
        timeout=1
    )
    time.sleep(2)  # allow Pico to reset
    print(f"[OK] Connected to {COM_PORT}")
except Exception as e:
    print("[ERROR] Could not open serial port")
    print(e)
    sys.exit(1)

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None

        for name in temps:
            for entry in temps[name]:
                if entry.current:
                    return int(entry.current)
    except Exception:
        pass

    return None

print("[INFO] Sending stats to Pico... Press CTRL+C to stop")

try:
    while True:
        cpu = int(psutil.cpu_percent(interval=None))
        ram = int(psutil.virtual_memory().percent)
        temp = get_cpu_temp()
        now = datetime.datetime.now().strftime("%H:%M:%S")

        payload = {
            "cpu": cpu,
            "ram": ram,
            "temp": temp if temp is not None else 0,
            "time": now,
            "status": "ONLINE"
        }

        message = json.dumps(payload) + "\n"
        ser.write(message.encode("utf-8"))

        print("→", payload)
        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:
    print("\n[STOPPED]")

finally:
    ser.close()
