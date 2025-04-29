import streamlit as st
import time
import serial
import serial.tools.list_ports
from modules.serial_manager import list_serial_ports
from modules.logger import create_session_folder, save_logs

# --- Page Configuration ---
st.set_page_config(page_title="LoRa Management Dashboard", page_icon="📡", layout="wide")

# --- Sidebar ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Serial Monitor", "Device Manager"])

# --- Main Area ---
st.title("📡 LoRa Arduino Management Dashboard")

if page == "Home":
    st.header("Home")
    st.markdown("Welcome to the **LoRa Management Dashboard**! Monitor devices and view incoming sensor data.")

elif page == "Serial Monitor":
    st.header("Live Serial Monitor")
    st.markdown("Real-time serial communication from connected LoRa Arduino devices.")

    available_ports = list_serial_ports()

    # --- Session State Initialization ---
    if "monitoring_active" not in st.session_state:
        st.session_state.monitoring_active = False
    if "serial_data" not in st.session_state:
        st.session_state.serial_data = {}
    if "serial_connections" not in st.session_state:
        st.session_state.serial_connections = {}
    if "selected_ports" not in st.session_state:
        st.session_state.selected_ports = []
    if "session_folder" not in st.session_state:
        st.session_state.session_folder = None

    baudrate = st.number_input("Baudrate", value=9600)

    # --- If NOT Monitoring: Show Device Selection ---
    if not st.session_state.monitoring_active:
        selected_ports = st.multiselect("Select Serial Ports", available_ports)
        st.session_state.selected_ports = selected_ports

        if st.button("Start Monitoring") and selected_ports:
            st.session_state.monitoring_active = True

            # Create a new session folder for logs
            st.session_state.session_folder = create_session_folder()

            # Open Serial Connections
            for port in selected_ports:
                try:
                    ser = serial.Serial(port, baudrate, timeout=1)
                    st.session_state.serial_connections[port] = ser
                    st.session_state.serial_data[port] = ""
                except Exception as e:
                    st.error(f"Failed to connect to {port}: {e}")

            st.rerun()

    # --- If Monitoring Active: Show Consoles ---
    else:
        st.success(f"Monitoring {', '.join(st.session_state.selected_ports)} at {baudrate} baudrate...")

        cols = st.columns(len(st.session_state.selected_ports))

        # --- Read Serial Data for Each Device ---
        from datetime import datetime
        for port, ser in st.session_state.serial_connections.items():
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.serial_data[port] += f"[{timestamp}] {line}\n"
                except:
                    pass

        # --- Display Each Console ---
        for idx, port in enumerate(st.session_state.selected_ports):
            with cols[idx]:
                st.markdown(f"**Console - {port}**")
                formatted_text = st.session_state.serial_data.get(port, "").replace("\n", "<br>")
                console_html = f"""
                <div style="background-color: black; color: #00FF00; padding: 10px; height: 300px; overflow-y: scroll; font-family: Courier, monospace; font-size: 14px;">
                {formatted_text}
                </div>
                """
                st.markdown(console_html, unsafe_allow_html=True)

        # --- Add a Spacer ---
        st.markdown("<br>", unsafe_allow_html=True)

        # --- Stop Monitoring Button ---
        if st.button("Stop Monitoring"):
            for ser in st.session_state.serial_connections.values():
                ser.close()

            # Save Logs Automatically
            if st.session_state.session_folder:
                save_logs(st.session_state.session_folder, st.session_state.serial_data)
                st.success(f"Logs saved to {st.session_state.session_folder}")

            st.session_state.monitoring_active = False
            st.session_state.serial_connections.clear()
            st.session_state.serial_data.clear()
            st.session_state.selected_ports.clear()
            st.session_state.session_folder = None
            st.rerun()

        # --- Auto Refresh Every Second ---
        time.sleep(1)
        st.rerun()

elif page == "Device Manager":
    st.header("🛠️ Device Manager")
    st.markdown("Manage connected LoRa devices here. (Coming Soon 🚀)")

# --- Footer ---
st.markdown("---")
st.caption("Developed with ❤️ by sumanxcodes")
