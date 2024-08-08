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
    if bit == '0':
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '1':
            m_code = 1 if bit == '0' else 2
    else:
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '0':
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            m_code = 3 if bit == '0' else 4
        else:
            bit, bit_string = read_and_pop(bit_string, 1)
            bit_len += 1
            if bit == '0':
                bit, bit_string = read_and_pop(bit_string, 1)
                bit_len += 1
                m_code = 5 if bit == '0' else 6
            else:
                bit, bit_string = read_and_pop(bit_string, 1)
                bit_len += 1
                if bit == '0':
                    m_code = 7
                else:
                    bit, bit_string = read_and_pop(bit_string, 1)
                    bit_len += 1
                    if bit == '0':
                        m_code = 8
                    else:
                        bit, bit_string = read_and_pop(bit_string, 1)
                        bit_len += 1
                        if bit == '0':
                            m_code = 9
                        else:
                            bit, bit_string = read_and_pop(bit_string, 1)
                            bit_len += 1
                            if bit == '0':
                                bit, bit_string = read_and_pop(bit_string, 1)
                                bit_len += 1
                                m_code = 10 if bit == '0' else 11
                            else:
                                bit, bit_string = read_and_pop(bit_string, 1)
                                bit_len += 1
                                if bit == '0':
                                    bit, bit_string = read_and_pop(bit_string, 1)
                                    bit_len += 1
                                    m_code = 12 if bit == '0' else 13
                                else:
                                    bit, bit_string = read_and_pop(bit_string, 1)
                                    bit_len += 1
                                    m_code = 14 if bit == '0' else 15
    return m_code, bit_string, bit_len


def huffman_3(bit_string):
    k = bit_len_map(3)
    m_code = 0
    bit, bit_string = read_and_pop(bit_string, 1)
    bit_len = 1
    if bit == '0':
        bit, bit_string = read_and_pop(bit_string, 1)
        bit_len += 1
        if bit == '1':
            m_code = 1
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
