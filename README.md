# LoRa Management Dashboard

This project is a **Streamlit**-based dashboard to manage, visualize, and monitor communication between Arduino devices over **LoRa**. It is designed to handle serial communication, display data in real-time, and provide basic analytics for received sensor information.

---

## 🚀 Project Setup

### 1. Clone the project folder
```bash
cd LoRa-mgmt-dashboard
```

### 2. Create and activate a virtual environment
```bash
# Create virtual environment
python3 -m venv lora-env

# Activate (macOS/Linux)
source lora-env/bin/activate

# Activate (Windows)
lora-env\Scripts\activate
```

### 3. Install dependencies
- Python 3.8+
- Streamlit
- pyserial
- pandas
- matplotlib
- plotly
- python-dotenv (optional)

Install all with:
```bash
pip install -r requirements.txt
```


### 4. Save dependencies
```bash
pip freeze > requirements.txt
```

### 5. Folder Structure
```bash
lora_dashboard/
├── lora_env/             # Virtual environment (excluded from Git)
├── app.py                # Main Streamlit app
├── requirements.txt      # Project dependencies
├── .env                  # (Optional) Configuration variables
├── README.md             # Project description
├── serial_manager.py     # (Optional) Serial communication handler
├── data/                 # Received data storage
│   ├── received_data.csv
└── assets/               # (Optional) Images, logos
```


### 7. Run the Streamlit app
```bash
streamlit run app.py
```
