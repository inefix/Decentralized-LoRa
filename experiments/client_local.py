import asyncio

add = "163.172.130.246"
port = 9999

message = b'\xd2\x84C\xa1\x01&\xa0Xr\xd0\x83XF\xa3\x01\x01\x05X\x1a000102030405060708090a0b0c\x00x#["0100", "0", "0x37dae2a4323e7028"]\xa0X%-b\xc8}l\xc6\x91#\x1bm?\x06\xd2\x13\x13ac\xd8\xa0@\xec\xa2\xc2!\xb0\xd3K)\x9b\xcc\xf1\x95\xaes\x19\xaa\xe7X@\xf4\x11\x1ayj\x1f\'\xf1/\xe8\x8fi6\x0eO\x95\xccE\xff\xb8\xbc7-ff\xf1\xdc\xf5m\xac\xf0qsH\x95\xc5\xc94\xe7\xae@\xab\x8f\x13\xa6u\xd9\xcf\xdc\xa0\xd4\x86\xa9\x88\xa3\xa2\x92\xc4m\xe3\x1a\xf4\xbf\xb0'

class EchoClientProtocol:
    def __init__(self, message, loop):
        self.message = message
        self.loop = loop
        self.transport = None

    def connection_made(self, transport):
        self.transport = transport
        print('Send:', self.message)
        #self.transport.sendto(self.message.encode())
        self.transport.sendto(self.message)

    def datagram_received(self, data, addr):
        #print("Received:", data.decode())
        print("Received:", data)

        print("Close the socket")
        self.transport.close()

    def error_received(self, exc):
        print('Error received:', exc)

    def connection_lost(self, exc):
        print("Socket closed, stop the event loop")
        loop = asyncio.get_event_loop()
        loop.stop()

print(f'Connecting to server on port : {port}')

loop = asyncio.get_event_loop()

connect = loop.create_datagram_endpoint(
    lambda: EchoClientProtocol(message, loop),
    remote_addr=(add, port))
transport, protocol = loop.run_until_complete(connect)

# loop.run_forever()
# transport.close()
# loop.close()
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()