import asyncio

add = "localhost"
port = 1680

class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)


loop = asyncio.get_event_loop()
print(f'Starting UDP server on port {port}')
# One protocol instance will be created to serve all client requests
listen = loop.create_datagram_endpoint(
    EchoServerProtocol, local_addr=(add, port))
transport, protocol = loop.run_until_complete(listen)


try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()