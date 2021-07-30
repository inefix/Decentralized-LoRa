import asyncio
# pip3 install pyserial-asyncio
from serial_asyncio import open_serial_connection
import sys
from binascii import unhexlify, hexlify

from lora import generate_deviceAdd, generate_key_pair, generate_key_sym, encrypt, sign, check_signature, decrypt

x_pub_server = "c29769136166eec1299e1b5d56c48de1787a3f72f0e8ee5c14357ef5b78fc6ea"
y_pub_server = "7666b00c308248cf824c8e224dd8ffcc4ccd1362c822f2ea82f5b01f79e1b49a"



async def write_keys(deviceAdd, x_pub_device, y_pub_device, private_value):
    global x_pub_server, y_pub_server
    # delete all the existing lines in file
    f = open("keys.txt", "w")
    f.write("")
    f.close()
    # write to file
    f = open("keys.txt", "a")
    f.write(f'deviceAdd:{deviceAdd}\n')
    f.write(f'x_pub_device:{x_pub_device}\n')
    f.write(f'y_pub_device:{y_pub_device}\n')
    f.write(f'private_value:{private_value}\n')
    f.write(f'x_pub_server:{x_pub_server}\n')
    f.write(f'y_pub_server:{y_pub_server}\n')
    f.close()

    print("deviceAdd : ", deviceAdd)
    print("x_pub_device : ", x_pub_device)
    print("y_pub_device : ", y_pub_device)



async def run(argv):
    global x_pub_server, y_pub_server

    try :

        if len(argv) == 1 and argv[0] == "-n":
            # generate a new device
            private_value, x_pub_device, y_pub_device = await generate_key_pair()
            deviceAdd = await generate_deviceAdd()
            await write_keys(deviceAdd, x_pub_device, y_pub_device, private_value)

        else :
            f = open("keys.txt", "r")
            temp = f.read().splitlines()
            f.close()
            if temp != []:
                deviceAdd = str(temp[0].split(":")[1])
                x_pub_device = str(temp[1].split(":")[1])
                y_pub_device = str(temp[2].split(":")[1])
                private_value = int(temp[3].split(":")[1])
                x_pub_server = str(temp[4].split(":")[1])
                y_pub_server = str(temp[5].split(":")[1])

            else :
                # generate a new device
                private_value, x_pub_device, y_pub_device = await generate_key_pair()
                deviceAdd = await generate_deviceAdd()
                await write_keys(deviceAdd, x_pub_device, y_pub_device, private_value)


        message = input('Message payload : ')

        key = await generate_key_sym(private_value, x_pub_server, y_pub_server)

        encrypted = await encrypt(key, deviceAdd, message)

        packet = await sign(private_value, x_pub_device, y_pub_device, encrypted)

        reader, writer = await open_serial_connection(url='/dev/serial0', baudrate=115200)

        packet_hex = hexlify(packet)
        writer.write(packet_hex + b'\n')
        await writer.drain()

        line = await reader.readline()
        line = line[:-1]
        # print("cleaned :", line)
        line_unhex = unhexlify(line)
        print("received :", line_unhex)


        if line_unhex != b'' and b'error' not in line_unhex :
            signature = await check_signature(x_pub_server, y_pub_server, line_unhex)

            if signature :
                print("Signature is correct")
                decrypted = await decrypt(line_unhex, key)
                print("Payload :", decrypted)
            else :
                print("Signature is not correct")


    except ValueError :
        print("ValueError")
        print('the lopy is not running device.py')
    except TypeError :
        print("TypeError")
        print('error, corrupted data')
    except AttributeError :
        print("AttributeError")
        print('error, corrupted data')
    except SystemError :
        print("SystemError")
        print('error, corrupted data')


    return


def main(argv):
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(run(argv))
    except KeyboardInterrupt:
        pass

    loop.close()



if __name__ == '__main__':
    main(sys.argv[1:])
