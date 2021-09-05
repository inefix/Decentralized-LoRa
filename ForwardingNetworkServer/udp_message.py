import json
from base64 import b64encode, b64decode

async def message_process(data) :
    size = len(data)

    if size < 12 :
        return b'error'
    else :
        if data[0] != 2 :
            return b'error'
        else :
            if data[3] != 0 :
                return b'error'
            else :
                string = data[12:].decode("utf-8")
                if "data" not in string or "867.500000" not in string or "4/7" not in string :
                    return b'error'
                else :
                    json_obj = json.loads(string)
                    final = json_obj['rxpk'][0]['data']
                    processed = b64decode(final)
                    print("Received message :", processed)

                    return processed


async def generate_response(data):
    data = b64encode(data)
    data = data.decode("utf-8")
    size_calc = await size_calculation(data)

    json_obj = {"txpk":{
        "imme":True,
        "rfch":0,
        "freq":867.5,
        "powe":14,
        "modu":"LORA",
        "datr":"SF12BW125",
        "codr":"4/7",
        "prea":8,
        "ipol":False,
        "size":size_calc,
        "ncrc":True,
        "data":data
    }}

    string = json.dumps(json_obj)
    response = b'\x02' + b'\x00' + b'\x00' + b'\x03' + string.encode("utf-8")

    return response


async def size_calculation(data):
    size = len(data)

    if size%4 == 0 and size >= 4 :  # potentially padded Base64
        if data[size-2] == "=" :    # 2 padding char to ignore
            return await size_calculation_nopad(size-2)
        elif data[size-1] == "=" :  # 1 padding char to ignore
            return await size_calculation_nopad(size-1)
        else :  # no padding to ignore
            return await size_calculation_nopad(size)

    else :  # treat as unpadded Base64
        return await size_calculation_nopad(size)


async def size_calculation_nopad(size):
    full_blocks = int(size / 4)
    last_chars = size % 4
    last_bytes = 0

    if last_chars == 0 :
        last_bytes = 0
    if last_chars == 2 :
        last_bytes = 1
    if last_chars == 3 :
        last_bytes = 2

    result_len = (3*full_blocks) + last_bytes

    return result_len
