import time

def size_calculation(data):
    size = len(data)

    if size%4 == 0 and size >= 4 :  # potentially padded Base64
        if data[size-2] == "=" :    # 2 padding char to ignore
            return size_calculation_nopad(size-2)
        elif data[size-1] == "=" :  # 1 padding char to ignore
            print(size)
            return size_calculation_nopad(size-1)
        else :  # no padding to ignore
            return size_calculation_nopad(size)

    else :  # treat as unpadded Base64
        return size_calculation_nopad(size)


def size_calculation_nopad(size):
    print(size)
    #size = len(data)
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


def main():
    data = "H3P3N2i9qc4yt7rK7ldqoeCVJGBybzPY5h1Dd7P7p8v"
    data2 = "YKQmASYAAAABltbdByk="
    data3 = "dGVzdA=="
    size = 32
    size2 = 14

    size_calc = size_calculation(data3)
    print(size_calc)

    t1 = 224760667
    t2 = 226760667
    dif = 2000000

    t3 = 217257603
    t4 = 222257603
    dif = 5000000

    t5 = 97787324
    t6 = 99787324
    dif = 2000000

    t7 = 41208756
    t8 = 53762372
    dif = 12553616

    t9 = 266431556
    t10 = 268431556
    dif = 2000000

    t = t10 - t9
    print(t)



if __name__ == '__main__':
    main()
