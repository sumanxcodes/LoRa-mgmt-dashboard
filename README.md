# LoRa Management Dashboard

This project is a **Streamlit**-based dashboard to manage, visualize, and monitor communication between Arduino devices over **LoRa**. It is designed to handle serial communication, display data in real-time, and provide basic analytics for received sensor information.

---

## 🚀 Project Setup

### 1. Clone the project folder
```bash
cd lora_dashboard
```

### 2. Create and activate a virtual environment
```bash
# Create virtual environment
python3 -m venv lora_env

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install streamlit pyserial python-dotenv pandas matplotlib plotly 
```

### 4. Save dependencies
```bash
pip freeze > requirements.txt
```

### 5. Folder Structure
```bash
lora_dashboard/
├── venv/                # Virtual environment (excluded from Git)
├── app.py
