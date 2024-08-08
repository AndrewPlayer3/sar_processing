def create_bit_string(bytes_string: str):
    bit_string = ''
    for byte in bytes_string:
        bit_string += '{:08b}'.format(byte)
    return bit_string


def read_and_pop(bit_string: str, bit_length: int):
    return bit_string[0:bit_length], bit_string[bit_length:]


def bit_len_map(brc: int):
    match brc:
        case 0:
            k = 4
        case 1:
            k = 5
        case 2:
            k = 7
        case 3:
            k = 10
        case 4:
            k = 16
        case other:
            raise ValueError(f'Invalid BRC Value Encountered in `bit_len_map`: {brc}')
    return k


# Avert your eyes.
def huffman_4(bit_string):
    k = bit_len_map(4)
    m_code = 0
    bit, bit_string = read_and_pop(bit_string, 1)
    bit_len = 1
    if bit == '0':  # 0 <-
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '0':  # 0 <- 0 <-
            return 0, bit_string, bit_len
        else:
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            return (1, bit_string, bit_len) if bit == '0' else (2, bit_string, bit_len)  # 0 or 1 <- 1 <- 0
    else:
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '0':
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            return (3, bit_string, bit_len) if bit == '0' else (4, bit_string, bit_len)  # 0 or 1 <- 1 <- 0
        else:
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            if bit == '0':
                bit, bit_string = read_and_pop(bit_string, 1)
                bit_len += 1
                return (5, bit_string, bit_len) if bit == '0' else (6, bit_string, bit_len)  # 0 or 1 <- 1 <- 0
            else:
                bit, bit_string = read_and_pop(bit_string, 1)
                bit_len += 1
                if bit == '0':
                    return 7, bit_string, bit_len
                else:
                    bit, bit_string = read_and_pop(bit_string, 1)
                    bit_len += 1
                    if bit == '0':
                        return 8, bit_string, bit_len
                    else:
                        bit, bit_string = read_and_pop(bit_string, 1)
                        bit_len += 1
                        if bit == '0':
                            return 9, bit_string, bit_len
                        else:
                            bit, bit_string = read_and_pop(bit_string, 1)
                            bit_len += 1
                            if bit == '0':
                                bit, bit_string = read_and_pop(bit_string, 1)
                                bit_len += 1
                                return (10, bit_string, bit_len) if bit == '0' else (11, bit_string, bit_len)
                            else:
                                bit, bit_string = read_and_pop(bit_string, 1)
                                bit_len += 1
                                if bit == '0':
                                    bit, bit_string = read_and_pop(bit_string, 1)
                                    bit_len += 1
                                    return (12, bit_string, bit_len) if bit == '0' else (13, bit_string, bit_len)
                                else:
                                    bit, bit_string = read_and_pop(bit_string, 1)
                                    bit_len += 1
                                    return (14, bit_string, bit_len) if bit == '0' else (15, bit_string, bit_len)
    


def huffman_3(bit_string):
    k = bit_len_map(3)
    m_code = 0
    bit, bit_string = read_and_pop(bit_string, 1)
    bit_len = 1
    if bit == '0':
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '0':
            return 0, bit_string, bit_len
        else:
            return 1, bit_string, bit_len
    else:
        m_code = 2
        for i in range(k - 3):
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            if bit == '0':
                break
            else:
                m_code += 1
        return m_code, bit_string, bit_len


def huffman(bit_string: str, brc: int):
    if brc == 3:
        return huffman_3(bit_string)
    elif brc == 4:
        return huffman_4(bit_string)
    else:
        bit_len = 0
        k = bit_len_map(brc)
        m_code = 0
        for i in range(k - 1):
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            if bit == '0':
                break
            else:
                m_code += 1
        return m_code, bit_string, bit_len