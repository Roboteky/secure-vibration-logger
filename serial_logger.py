import serial
import time
from cryptography.fernet import Fernet
import os
from datetime import datetime

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

# Load or create encryption key
if not os.path.exists("secret.key"):
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
else:
    with open("secret.key", "rb") as key_file:
        key = key_file.read()

fernet = Fernet(key)

# Adjust COM port if needed
ser = serial.Serial('COM7', 9600, timeout=1)
time.sleep(2)

with open("data/data.enc", "ab") as log_file:
    print("Logging started...")
    while True:
        line = ser.readline().decode().strip()
        if line:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"[{timestamp}] {line}"
            encrypted = fernet.encrypt(message.encode())
            log_file.write(encrypted + b"\n")
            print(f"[LOGGED] {message}")
