'''
serial_uart_driver.py

Sample Python driver for RS-232C serial UART communication using pyserial.
Provides initialization, connection, disconnection, and connection testing.
Requires: pip install pyserial
'''

import serial
import time

class SerialDriver:
    def __init__(self, port: str, baudrate: int = 19200, timeout: float = 1.0):
        """
        Initialize the serial driver.
        :param port: Serial port device name (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
        :param baudrate: Communication speed (bits per second)
        :param timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial = None

    def connect(self) -> bool:
        """
        Open the serial port with the configured settings.
        :return: True if connection succeeds, False otherwise
        """
        try:
            self._serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_TWO
            )
            # small delay for port to settle
            time.sleep(0.1)
            return self._serial.is_open
        except serial.SerialException as e:
            print(f"Failed to open serial port {self.port}: {e}")
            return False

    def disconnect(self):
        """
        Close the serial port if it is open.
        """
        if self._serial and self._serial.is_open:
            self._serial.close()

    def is_connected(self) -> bool:
        """
        Check if the serial port is currently open.
        :return: True if open, False otherwise
        """
        return bool(self._serial and self._serial.is_open)

    def send(self, data: bytes) -> int:
        """
        Send raw bytes to the serial device.
        :param data: Bytes to send
        :return: Number of bytes written
        """
        if not self.is_connected():
            raise serial.SerialException("Attempt to write when serial port is not open")
        return self._serial.write(data)

    def receive(self, size: int = 1) -> bytes:
        """
        Read bytes from the serial device.
        :param size: Number of bytes to read
        :return: Bytes read
        """
        if not self.is_connected():
            raise serial.SerialException("Attempt to read when serial port is not open")
        return self._serial.read(size)

    def test_connection(self) -> bool:
        """
        Test the connection by checking the port state.
        Optionally, you could send a heartbeat or ping command here if supported.
        :return: True if the port is open and responsive, False otherwise
        """
        return self.is_connected()


if __name__ == "__main__":
    # Example usage
    driver = SerialDriver(port='COM10', baudrate=19200, timeout=0.5)
    if driver.connect():
        print("Connection established.")
        # send a test command, e.g., b'?\r\n'
        try:
            driver.send(b'1LOG IN\r\n')
            response = driver.receive(64)
            print(f"Received: {response}")
        except Exception as e:
            print(f"Communication error: {e}")
        finally:
            driver.send(b'TURRET 1\r\n')

            time.sleep(1)
            driver.disconnect()
            print("Disconnected.")
    else:
        print("Unable to open serial port.")
