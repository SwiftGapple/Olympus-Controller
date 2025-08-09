import serial
import time

class OlympusTurretController:
    """
    Controller API for Olympus BX2 turret via RS-232C (USB-serial).
    """

    def __init__(self, port: str,
                 baudrate: int = 19200,
                 bytesize: int = serial.EIGHTBITS,
                 parity: str = serial.PARITY_EVEN,
                 stopbits: int = serial.STOPBITS_TWO,
                 timeout: float = 1.0,
                 index: str = '1',
                 terminator: bytes = b'\r\n'):
        """
        Initialize serial port to match DIP-switch settings.
        """
        self.index = index
        self.terminator = terminator
        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity,
            stopbits=stopbits,
            timeout=timeout,
            rtscts=True
        )
        # wait for CTS to go high (initialization complete)
        start = time.time()
        while not self.ser.getCTS():
            if time.time() - start > timeout:
                raise TimeoutError("CTS did not assert—check power/initialization.")
            time.sleep(0.01)

    def close(self):
        """Close the serial connection."""
        self.ser.close()

    def _send_command(self, tag: str, data: str = None, query: bool = False) -> str:
        """
        Build and send a command, then read one line of response.
        """
        if query:
            cmd = f"{self.index}{tag}?".encode('ascii') + self.terminator
        elif data is not None:
            # space between tag and data
            cmd = f"{self.index}{tag} {data}".encode('ascii') + self.terminator
        else:
            cmd = f"{self.index}{tag}".encode('ascii') + self.terminator

        self.ser.reset_input_buffer()
        self.ser.write(cmd)
        # read until terminator
        resp = self.ser.read_until(self.terminator).decode('ascii', errors='ignore').strip()
        return resp

    def login(self):
        """
        Switch to remote mode.
        Sends: 'LOG IN'
        """
        resp = self._send_command('LOG', 'IN')
        if '+' not in resp:
            raise RuntimeError(f"Login failed: {resp}")
        return resp

    def logout(self):
        """
        Switch back to local mode.
        Sends: 'LOG OUT'
        """
        resp = self._send_command('LOG', 'OUT')
        if '+' not in resp:
            raise RuntimeError(f"Logout failed: {resp}")
        return resp

    def set_turret(self, position: int):
        """
        Engage the turret to position 1–8.
        Sends: 'TURRET p1'
        """
        if not 1 <= position <= 8:
            raise ValueError("Position must be between 1 and 8.")
        resp = self._send_command('TURRET', str(position))
        if '+' not in resp:
            raise RuntimeError(f"Failed to set turret: {resp}")
        return resp

    def get_turret(self) -> int:
        """
        Query current turret position.
        Sends: 'TURRET?'
        Returns the integer position.
        """
        resp = self._send_command('TURRET', query=True)
        # Resp format is something like '1TURRET 3' or '1TURRET 3'
        parts = resp.replace(' ', '').split('TURRET')
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])
        raise RuntimeError(f"Unexpected turret status response: '{resp}'")

# Example usage:
if __name__ == "__main__":
    ctrl = OlympusTurretController(port="COM10", baudrate=19200)
    try:
        ctrl.login()
        print("Logged into remote mode.")
        ctrl.set_turret(2)
        print("Turret moved to position 2.")
        pos = ctrl.get_turret()
        print(f"Current turret position is {pos}.")
        ctrl.logout()
        print("Returned to local mode.")
    finally:
        ctrl.close()
