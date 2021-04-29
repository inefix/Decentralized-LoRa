"""UDP proxy server."""
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df

import asyncio
import base64

local_addr = "0.0.0.0"
local_port = 1680

remote_host = "163.172.130.246"
remote_port = 9999


async def process(data) :
    size = len(data)
    #print(data[3])
    print(f'{data} {type(data)} {size}')

    if size < 12 :
        print(" (too short for GW <-> MAC protocol)\n")
        return b'error'
    else :
        print("Process the data 1")
        if data[0] != 2 :
            print("invalid version\n")
            return b'error'
        else :
            print("Process the data 2")
            if data[3] != 0 :
                print("Not the right gateway command")
                return b'error'
            else :
                print("Process the data 3")
                #print(data[len(data)-10])
                string = str(data)
                if "data" not in string and "868.500000" not in string :
                    print("No data field and not the right freq")
                    return b'error'
                else :
                    print("Process the data 4")
                    #print(string)
                    tableau = string.split("{")
                    #print(tableau)
                    tableau[2] = tableau[2][:-2]
                    #print(tableau[2])
                    tableau = tableau[2].split(",")
                    nice_data = tableau[len(tableau)-1]
                    #print(nice_data)
                    if "data" not in nice_data :
                        print("No data field")
                        return b'error'
                    else :
                        print("Process the data 5")
                        nice_data = nice_data.split(":")
                        #print(nice_data[1])
                        final = nice_data[1][1:]
                        final = final[:-1]
                        print(final)
                        print(base64.b64decode(final))

                        return final



class ProxyDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, remote_address):
        self.remote_address = remote_address
        self.remotes = {}
        super().__init__()

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, addr)) 

    async def datagram_received_async(self, data, addr):
        #print('Received \x1b[0;30;46m%s\x1b[0m from %s' % (data, addr))
        #print("Received from device :", data)
        processed = await process(data)
        if processed != b'error':
            data = processed
            # a = bytearray(data)
            # a[3] = 4
            # data = bytes(a)
            # print(data)
            # self.transport.sendto(data, addr)
            # print("data sent to :", addr)
            if addr in self.remotes:
                self.remotes[addr].transport.sendto(data)
                return
            loop = asyncio.get_event_loop()
            #print("Device addr :", addr)
            self.remotes[addr] = RemoteDatagramProtocol(self, addr, data)
            coro = loop.create_datagram_endpoint(
                lambda: self.remotes[addr], remote_addr=self.remote_address)
            asyncio.ensure_future(coro)


class RemoteDatagramProtocol(asyncio.DatagramProtocol):

    def __init__(self, proxy, addr, data):
        self.proxy = proxy
        self.addr = addr
        self.data = data
        super().__init__()

    def connection_made(self, transport):
        loop = asyncio.get_event_loop()
        loop.create_task(self.connection_made_async(transport)) 

    async def connection_made_async(self, transport):
        self.transport = transport
        #print("Received from device :", self.data)
        self.transport.sendto(self.data)

    def datagram_received(self, data, _):
        loop = asyncio.get_event_loop()
        loop.create_task(self.datagram_received_async(data, _)) 

    async def datagram_received_async(self, data, _):
        print("Received from server :", data)
        self.proxy.transport.sendto(data, self.addr)

    def connection_lost(self, exc):
        #self.proxy.remotes.pop(self.attr)
        self.proxy.remotes.pop(self.addr)


async def start_datagram_proxy(bind, port, remote_host, remote_port):
    loop = asyncio.get_event_loop()
    # connect to remote host
    protocol = ProxyDatagramProtocol((remote_host, remote_port))
    # launch server
    return await loop.create_datagram_endpoint(
        lambda: protocol, local_addr=(bind, port))


def main(bind=local_addr, port=local_port, remote_host=remote_host, remote_port=remote_port):
    loop = asyncio.get_event_loop()
    print("Starting UDP proxy server...")
    coro = start_datagram_proxy(bind, port, remote_host, remote_port)
    transport, _ = loop.run_until_complete(coro)
    print("UDP proxy server is running...")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    print("Closing transport...")
    transport.close()
    loop.close()


if __name__ == '__main__':
    main()