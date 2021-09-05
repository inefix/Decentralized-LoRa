from machine import UART
import time
import ubinascii

# this uses the UART_1 default pins for TXD and RXD (``P3`` and ``P4``)
uart = UART(1, baudrate=115200)

message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'

while True :
    buffer = uart.readline()
    print(buffer)
    if buffer != None :
        buffer = buffer[:-1]
        print(buffer)
        buffer_unhex = ubinascii.unhexlify(buffer)
        print(buffer_unhex)
        print(buffer_unhex == message)

        # send buffer_unhex via lora

        # get the response

        # send the response back via uart

        uart.write(buffer + b'\n')
    time.sleep(5)
