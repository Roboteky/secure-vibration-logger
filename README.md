# Secure Vibration Logger

Logs vibration events from Arduino Nano securely with encrypted storage and a secure Flask dashboard.

## Components
- Arduino Nano
- Digital vibration sensor (D2)
- Python with Flask + cryptography

## Usage

### 1. Upload to Arduino
Use `vibration_logger.ino`.

### 2. Install Python Requirements
```bash
pip install pyserial cryptography flask flask-httpauth
```

### 3. Start Serial Logger
```bash
python serial_logger.py
```

### 4. Start Flask Viewer
In another terminal:
```bash
python app.py
```

Then visit https://127.0.0.1:5000/data  
Login: `admin` / `pass123`

## Encrypted Logs
Stored in `data/data.enc` using Fernet AES.
