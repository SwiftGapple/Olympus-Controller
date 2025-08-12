import serial
import time

class OlympusNosepiece:
    """
    Controller for Olympus U-D6REMC nosepiece via BX-REMCB RS-232.
    """
    def __init__(self, port: str):
        # Open serial port with correct settings
        self.ser = serial.Serial(
            port=port,
            baudrate=19200,                     # BX-REMCB default baudrate
            bytesize=serial.EIGHTBITS,          # 8 data bits
            parity=serial.PARITY_EVEN,          # Even parity
            stopbits=serial.STOPBITS_TWO,       # 2 stop bits
            rtscts=True,                        # RTS/CTS hardware flow
            xonxoff=False,                      # No software flow
            timeout=1                           # 1 s read timeout
        )
        time.sleep(0.1)  # Allow port to stabilize

    def login(self):
        """Enable objective control channel."""
        self.ser.write(b'1LOG IN\r\n')
        resp = self.ser.readline().decode().strip()
        print(f"Login response: '{resp}'")
        return resp  # Expect "1LOG +"

    def logout(self):
        """Disable objective control channel."""
        self.ser.write(b'1LOG OUT\r\n')
        resp = self.ser.readline().decode().strip()
        print(f"Logout response: '{resp}'")
        return resp  # Expect "1LOG -"

    def test_connection(self) -> bool:
        """Test if the device is responsive."""
        try:
            # Try to get current objective position
            self.get_objective()
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False

    def set_objective(self, n: int):
        """
        Move nosepiece to position n (1–6).
        Returns True if acknowledged by querying afterward.
        """
        cmd = f'1OB {n}\r\n'.encode()
        self.ser.write(cmd)
        time.sleep(0.2)
        return self.get_objective() == n

    def get_objective(self) -> int:
        """Query current objective position; returns the integer position."""
        self.ser.write(b'1OB?\r\n')
        resp = self.ser.readline().decode().strip()
        
        # Debug: print the raw response
        print(f"Raw response: '{resp}' (length: {len(resp)})")
        
        # Handle empty response
        if not resp:
            raise RuntimeError("Empty response from device - device may not be connected or responding")
        
        # resp format: "1OB <n>"
        try:
            parts = resp.split()
            if len(parts) < 2:
                raise RuntimeError(f"Response too short: '{resp}'")
            return int(parts[1])
        except (IndexError, ValueError) as e:
            raise RuntimeError(f"Unexpected response format: '{resp}' - {e}")

    def close(self):
        """Close the serial port."""
        self.ser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



try:
    with OlympusNosepiece(port='COM10') as np_ctrl:
        print("Testing connection...")
        if not np_ctrl.test_connection():
            print("Error: Device not responding. Check:")
            print("  - Device is powered on")
            print("  - Serial cable is connected")
            print("  - COM port is correct")
            exit(1)
        
        print("Connection successful!")
        print(np_ctrl.login())           # Enable control (→ "1LOG +")
        
        try:
            success = np_ctrl.set_objective(2)
            print("Moved to 2:", success)
            print("Current pos:", np_ctrl.get_objective())
        except Exception as e:
            print(f"Error during objective movement: {e}")
        
        print(np_ctrl.logout())          # Disable control (→ "1LOG -")

except serial.SerialException as e:
    print(f"Serial port error: {e}")
    print("Check if COM7 is available and not in use by another application")
except Exception as e:
    print(f"Unexpected error: {e}")
