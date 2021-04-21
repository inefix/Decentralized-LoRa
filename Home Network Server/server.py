"""UDP server"""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df
# https://docs.python.org/3/library/asyncio-protocol.html

import asyncio
from aiohttp import web
import aiohttp_cors

add = "0.0.0.0"     # localhost does not work ! https://stackoverflow.com/questions/15734219/simple-python-udp-server-trouble-receiving-packets-from-clients-other-than-loca/15734249
port = 9999



def test(request):
    print("test")


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



app = web.Application()

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
})

cors.add(app.router.add_get('', test))



def main(add=add, port=port):
    loop = asyncio.get_event_loop()
    print("Starting UDP server...")
    con = start_datagram_proxy(add, port)
    transport, _ = loop.run_until_complete(con)
    print("UDP server is running...")
    print("Start HTTP server...")
    loop.run_until_complete(web.run_app(app, port=80))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()