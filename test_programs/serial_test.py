# Usart Library
import serial

import datetime
import time as t

Usart = serial.Serial(
            port='COM9',
            baudrate=19200,                     # BX-REMCB default baudrate
            bytesize=serial.EIGHTBITS,          # 8 data bits
            parity=serial.PARITY_EVEN,          # Even parity
            stopbits=serial.STOPBITS_TWO,       # 2 stop bits
            rtscts=True,
            #xonxoff=False,                        # RTS/CTS hardware flow             # No software flow
            timeout=1                           # 1 s read timeout
        )
t.sleep(1)


while True:    # Check the CTS signal state
    if Usart.getCTS():
        print("CTS asserted (ready to receive)")
        break
    else:   
        print("CTS de-asserted (not ready)")

    t.sleep(0.5)
    break