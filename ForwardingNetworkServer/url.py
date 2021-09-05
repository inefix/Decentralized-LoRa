async def url_process(url) :
    add = url.split(":")

    # if IPv4
    if len(add) < 4 :
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
        return address, port

    # if IPv6
    else :
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

        address = ':'.join(add[:-1])
        address = address.replace("/", "")
        address = address.replace(" ", "")
        port = add[len(add)-1]
        port = int(port)
        return address, port
