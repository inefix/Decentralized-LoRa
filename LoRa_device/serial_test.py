from asyncio import get_event_loop
from serial_asyncio import open_serial_connection
from binascii import unhexlify, hexlify

async def run():
    reader, writer = await open_serial_connection(url='/dev/serial0', baudrate=115200)
    while True:
        message = b'\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0011", "0", "0x1145f03880d8a975"]\xa1\x0b\x83C\xa1\x01&\xa0X@\x92\xc9\xb2v\xa4\xaa\xd3s+\x8a\xebT\xdc\x07o\xf5NH\xe8 Rz4\x82\xe3H\x18\x97\x15\xb6Z\x1c\x97$X\\H\xd8\x88/aC\x15\x9d\x07\x93\x1ftG\xd1\xa2T\xb5\x9eB\xe0^J\xcb\x82\xd8\xccN\rUk\xe5(J\x13\rz\xf3\xf7\xbe\xb3\xa7\xc4\x88\xc1\xe9\xbf\xaaM\xc8i'
        message_hex = hexlify(message)
        writer.write(message_hex + b'\n')
        await writer.drain()
        line = await reader.readline()
        print(line)
        line = line[:-1]
        print(line)
        line_unhex = unhexlify(line)
        print(line_unhex)
        print(line_unhex == message)

loop = get_event_loop()
loop.run_until_complete(run())
