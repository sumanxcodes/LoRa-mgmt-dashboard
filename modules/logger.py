import os
from datetime import datetime

def create_session_folder():
    """Create a new folder for the current session logs."""
    session_time = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    session_folder = os.path.join("logs", session_time)
    os.makedirs(session_folder, exist_ok=True)
    return session_folder

def save_logs(session_folder, serial_data):
    """Save serial data for each device into separate log files."""
    for port, data in serial_data.items():
        filename = port.replace("/", "_").replace(".", "_")
        filepath = os.path.join(session_folder, f"{filename}.txt")
        with open(filepath, "w") as f:
            f.write(data)
