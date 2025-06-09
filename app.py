import streamlit as st
import time
import serial
import random
import string
from modules.serial_manager import list_serial_ports
from modules.logger import create_session_folder, save_logs



def generate_uuid(prefix):
    uuid_part = ''.join(random.choices('0123456789ABCDEF', k=8))
    return (prefix + uuid_part).upper()

def generate_seed():
    return random.randint(100000000, 999999999)

def write_device_info_to_eeprom(port, prefix="TX", baudrate=9600):
    device_id = generate_uuid(prefix)
    seed = generate_seed()
    command = f"WRITE_INFO:{device_id},{seed}\n"

    try:
        with serial.Serial(port, baudrate, timeout=2) as ser:
            ser.write(command.encode('utf-8'))
            response = ser.readline().decode('utf-8').strip()
            if response == f"INFO_UPDATED:{device_id},{seed}":
                print(f"Written to EEPROM: {device_id}, Seed: {seed}")
            else:
                print(f"Unexpected response: {response}")
    except Exception as e:
        print(f" Error sending data: {e}")



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
        for port in st.session_state.selected_ports:
            # with cols[idx]:
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
    st.markdown("View and update seed values stored in EEPROM on the device.")

    available_ports = list_serial_ports()
    selected_port = st.selectbox("Select Device", available_ports)
    baudrate = st.number_input("Baudrate", value=9600, key="dm_baud")

    # --- Init State Flags ---
    if "eeprom_write_triggered" not in st.session_state:
        st.session_state.eeprom_write_triggered = False
    if "uuid_was_refreshed" not in st.session_state:
        st.session_state.uuid_was_refreshed = False
    if "seed_was_refreshed" not in st.session_state:
        st.session_state.seed_was_refreshed = False
    if "show_success_once" not in st.session_state:
        st.session_state.show_success_once = False

    # ✅ Show success message if flagged (one-time)
    if st.session_state.show_success_once:
        st.success(f"✅ EEPROM updated: {st.session_state.eeprom_id}, {st.session_state.eeprom_seed}")
        st.session_state.show_success_once = False
        st.stop()

    # --- Init Generated State ---
    if "device_prefix" not in st.session_state:
        st.session_state.device_prefix = "TX"
    if "uuid_suffix" not in st.session_state:
        st.session_state.uuid_suffix = ''.join(random.choices('0123456789ABCDEF', k=8))
    if "generated_uuid" not in st.session_state:
        st.session_state.generated_uuid = st.session_state.device_prefix + st.session_state.uuid_suffix
    if "generated_seed" not in st.session_state:
        st.session_state.generated_seed = generate_seed()
    if "eeprom_id" not in st.session_state:
        st.session_state.eeprom_id = None
    if "eeprom_seed" not in st.session_state:
        st.session_state.eeprom_seed = None
    if "eeprom_raw" not in st.session_state:
        st.session_state.eeprom_raw = None

    def generate_full_uuid():
        return (st.session_state.device_prefix + st.session_state.uuid_suffix).upper()

    def update_uuid_prefix():
        st.session_state.generated_uuid = generate_full_uuid()

    # --- EEPROM Read ---
    if selected_port and not st.session_state.eeprom_write_triggered:
        try:
            ser = serial.Serial(selected_port, baudrate, timeout=2)
            ser.write(b"READ_EEPROM\n")
            response = ser.readline().decode('utf-8').strip()
            ser.close()
            if "ID:" in response and "SEED:" in response:
                parts = response.replace("ID:", "").replace("SEED:", "").split(",")
                uuid_read = parts[0].strip()
                seed_read = parts[1].strip()

                st.session_state.eeprom_id = uuid_read
                st.session_state.eeprom_seed = seed_read
                st.session_state.eeprom_raw = response

                if not st.session_state.uuid_was_refreshed:
                    st.session_state.generated_uuid = uuid_read
                    st.session_state.device_prefix = uuid_read[:2]
                    st.session_state.uuid_suffix = uuid_read[2:]
                if not st.session_state.seed_was_refreshed:
                    st.session_state.generated_seed = int(seed_read)

        except Exception as e:
            st.error(f"Error reading EEPROM: {e}")

    # --- EEPROM Display ---
    if st.session_state.eeprom_raw:
        st.code(st.session_state.eeprom_raw, language='text')
    if st.session_state.eeprom_id:
        st.markdown(f"**Device ID:** <span style='color:green;font-weight:bold;'>{st.session_state.eeprom_id}</span>", unsafe_allow_html=True)
    if st.session_state.eeprom_seed:
        st.markdown(f"**Current Seed:** <span style='color:green;font-weight:bold;'>{st.session_state.eeprom_seed}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # --- UUID Section ---
    st.subheader("🔖 Device Identifier (UUID)")
    st.markdown("Each device gets a unique identifier. You can change the prefix or generate a new one.")

    uuid_row1, uuid_row2 = st.columns([6, 1])
    with uuid_row2:
        st.markdown(" ")
        if st.button("🔄 New UUID", key="refresh_uuid"):
            st.session_state.uuid_suffix = ''.join(random.choices('0123456789ABCDEF', k=8))
            st.session_state.generated_uuid = generate_full_uuid()
            st.session_state.uuid_was_refreshed = True
    with uuid_row1:
        st.text_input("Generated Device ID", value=st.session_state.generated_uuid, key=f"uuid_display_{st.session_state.generated_uuid}", disabled=True)

    st.selectbox("Prefix", ["TX", "RX", "RL"], key="device_prefix", on_change=update_uuid_prefix)

    st.markdown("---")

    # --- Seed Section ---
    st.subheader("🌱 Cryptographic Seed")
    st.markdown("Used to generate secure keys for the device during Diffie-Hellman exchange.")

    seed_row1, seed_row2 = st.columns([6, 1])
    with seed_row2:
        st.markdown(" ")
        if st.button("🔄 New Seed", key="refresh_seed"):
            st.session_state.generated_seed = generate_seed()
            st.session_state.seed_was_refreshed = True
    with seed_row1:
        st.text_input("Generated Seed", value=str(st.session_state.generated_seed), key=f"seed_display_{st.session_state.generated_seed}", disabled=True)

    st.markdown(" ")

    # --- EEPROM Write Trigger ---
    if st.button("✍️ Write to EEPROM"):
        st.session_state.eeprom_write_triggered = True
        st.rerun()

    # --- EEPROM Write Execution ---
    if st.session_state.eeprom_write_triggered:
        st.session_state.eeprom_write_triggered = False
        try:
            ser = serial.Serial(selected_port, baudrate, timeout=2)
            cmd = f"WRITE_INFO:{st.session_state.generated_uuid},{st.session_state.generated_seed}\n"
            ser.write(cmd.encode('utf-8'))
            response = ser.readline().decode('utf-8').strip()
            ser.close()

            if response.startswith("INFO_UPDATED:"):
                st.session_state.eeprom_id = st.session_state.generated_uuid
                st.session_state.eeprom_seed = str(st.session_state.generated_seed)
                st.session_state.eeprom_raw = f"ID:{st.session_state.eeprom_id},SEED:{st.session_state.eeprom_seed}"
                st.session_state.uuid_was_refreshed = False
                st.session_state.seed_was_refreshed = False
                st.session_state.show_success_once = True
                st.rerun()
            else:
                st.warning(f"⚠️ Unexpected response: {response}")
        except Exception as e:
            st.error(f"Failed to write EEPROM: {e}")
