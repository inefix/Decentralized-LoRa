"""UDP server"""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
# https://docs.python.org/3/library/asyncio-protocol.html

import asyncio

add = "localhost"
port = 9999

class EchoServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        message = data.decode()
        print('Received %r from %s' % (message, addr))
        print('Send %r to %s' % (message, addr))
        self.transport.sendto(data, addr)


async def start_datagram_proxy(add, port):
    loop = asyncio.get_event_loop()
    return await loop.create_datagram_endpoint(
        lambda: EchoServerProtocol(),
        local_addr=(add, port))


def main(add=add, port=port):
    loop = asyncio.get_event_loop()
    print("Starting UDP server...")
    coro = start_datagram_proxy(add, port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP server is running...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()