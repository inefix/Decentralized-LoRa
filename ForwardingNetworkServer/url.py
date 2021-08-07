async def url_process(url) :
    # ip4 = "https://111.111.111.111:65535"
    # ip4 = "111.111.111.111:65535"
    # print(len(ip4))

    # ip6 = "https://[0:0:0:0:0:0:0:1]:123"
    # ip6 = "[0:0:0:0:0:0:0:1]:123"
    # print(len(ip6))

    add = url.split(":")

    # if IPv4
    if len(add) < 4 :
        # print("ipv4")
        # port + http
        if len(add) > 2 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
        # only address --> no port
        elif len(add) == 1 :
            address = add[0]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 2 and "http" in add[0] :
            address = add[len(add)-1]
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port

        address = add[0]
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port

    # if IPv6
    else :
        # print("ipv6")
        # port + http
        if len(add) > 9 and "http" in add[0] :
            # contain "http://" or "https://"
            add.pop(0)
            add[0] = add[0].replace("/", "")
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")
        # only address
        elif len(add) == 8 :
            address = ':'.join(add)
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + http
        elif len(add) == 9 and "http" in add[0] :
            address = ':'.join(add[1:])
            address = address.replace("/", "")
            address = address.replace(" ", "")
            port = 0
            return address, port
        # address + port
        elif len(add) == 9 and "http" not in add[0] :
            add[0] = add[0].replace("[", "")
            add[len(add)-2] = add[len(add)-2].replace("]", "")

        # print(add)
        address = ':'.join(add[:-1])
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        # print(address)
        # print(port)
        return address, port
