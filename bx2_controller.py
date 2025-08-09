# Usart Library
import serial
import sys
import datetime
import time as t

# # Init serial port
# Usart = serial.Serial(
#     #port='/dev/ttyUSB0',
#     port='COM7',
#     baudrate=9600,
#     bytesize=serial.SEVENBITS,
#     parity=serial.PARITY_ODD,
#     stopbits=serial.STOPBITS_ONE,
#     timeout=1)

print("Starting BX-REMCB controller")

Usart = serial.Serial(
            port='COM10',
            baudrate=19200,                     # BX-REMCB default baudrate
            bytesize=serial.EIGHTBITS,          # 8 data bits
            parity=serial.PARITY_EVEN,          # Even parity
            stopbits=serial.STOPBITS_TWO,       # 2 stop bits
            #rtscts=False,
            #xonxoff=False,                        # RTS/CTS hardware flow             # No software flow
            timeout=1                           # 1 s read timeout
        )

# Usart = serial.Serial(
#     port='COM9',
#     baudrate=19200,
#     timeout=1)


if Usart.getCTS():
    print("CTS asserted (ready to receive)")
else:
    print("CTS de-asserted (not ready)")
    # sys.exit(1)

t.sleep(1)

# Usart.setCTS(True)
# while True:    # Check the CTS signal state
#     if Usart.getCTS():
#         print("CTS asserted (ready to receive)")
#         break
#     else:   
#         print("CTS de-asserted (not ready)")

#     t.sleep(0.5)
#     break


#t.sleep(1) # Wait for a second before checking again


# if Usart.getCTS():
#     print("CTS asserted (ready to receive)")
# else:   
#     print("CTS de-asserted (not ready)")



time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(time)

# Usart.write(b'1LOG IN\r\n') 
# Usart.write("1OB 1\r\n".encode())
# Usart.write(b'1LOG OUT\r\n') 
# Usart.close()
# exit()

try:
    inital_time = t.time()
    # send LOG IN so the frame will accept motion commands
    #Usart.write(b'1LOG IN\r\n')      # note the \r\n terminator
    
    # Check Log Status
    Usart.write('1LOG?\r\n'.encode())      # note the \r\n terminator
    current_response = Usart.readline()
    print(f"Log Status: {current_response}")

    while True:
        Usart.write('1LOG IN\r\n'.encode())      # note the \r\n terminator
        current_response = Usart.readline()
        print(f"Waiting for LOG IN | {current_response}")
        
        if current_response == b'LOG +\r\n':
            print("LOG IN successful!")
            break
            
        t.sleep(0.5)
        if t.time() - inital_time > 10:
            print("Timeout")
            break
    
    
    t.sleep(0.5)
    # move the six-place nosepiece to position 1
    Usart.write("OB 1\r\n".encode())

    t.sleep(0.5)
    # move the six-place nosepiece to position 1
    Usart.write("OB 2\r\n".encode())

    t.sleep(0.5)
    # move the six-place nosepiece to position 1
    Usart.write("OB 3\r\n".encode())
    

    # read back the acknowledgement
    ack = Usart.readline()           # → b'1OB +\r\n' on success
    print(ack)

    t.sleep(0.5)

    ack = Usart.readline()           # → b'1OB +\r\n' on success
    print(ack)

    print("Write done")

    Usart.close()
except KeyboardInterrupt:
    Usart.close()