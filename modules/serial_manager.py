# modules/serial_manager.py

import serial
import serial.tools.list_ports

def list_serial_ports():
    """List available serial ports."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def read_serial_line(port, baudrate=9600, timeout=1):
    """Reads a single line from the selected serial port."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        line = ser.readline().decode('utf-8').strip()
        ser.close()
        return line
    except Exception as e:
        return f"Error reading serial: {e}"
