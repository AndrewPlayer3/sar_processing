from structs import (
    PRIMARY_HEADER_SIZE,
    SECONDARY_HEADER_SIZE,
    WORD_SIZE,
    PRIMARY_HEADER,
    PRIMARY_HEADER_FIELDS,
    SECONDARY_HEADER,
    SECONDARY_HEADER_FIELDS,
    SUB_COMM_KEY_POS,
    SUB_COMM_KEY_VAL,
)

from packet import Packet


def get_header_dict(header_bytes, header_bit_lengths, header_field_names):
    read_and_pop = lambda bit_string, bit_length: (bit_string[0:bit_length], bit_string[bit_length:])
    bit_string = ''
    for byte in header_bytes:
        bit_string += '{:08b}'.format(byte)

    header_value_array = []
    for bit_len in header_bit_lengths:
        header_field_value, bit_string = read_and_pop(bit_string, bit_len)
        header_value_array.append(header_field_value) 

    index = 0
    header_dict = {}
    for field in header_field_names:
        if index >= len(header_field_names) or index >= len(header_value_array):
            raise ValueError('The number of field names and header values does not match.')
        header_dict[field] = header_value_array[index]
        index += 1

    return header_dict


def packet_generator(raw_data):
    while raw_data:
        primary_header_bytes = raw_data.read(PRIMARY_HEADER_SIZE)
        primary_header = get_header_dict(primary_header_bytes, PRIMARY_HEADER, PRIMARY_HEADER_FIELDS)
        secondary_header_bytes = raw_data.read(SECONDARY_HEADER_SIZE)
        secondary_header = get_header_dict(secondary_header_bytes, SECONDARY_HEADER, SECONDARY_HEADER_FIELDS)
        packet_data_length = primary_header['packet_data_length']
        user_data = None
        if packet_data_length:
            packet_data_length = int(packet_data_length, 2)
            user_data_length = (packet_data_length + 1) - SECONDARY_HEADER_SIZE
            if user_data_length > 0:
                user_data = raw_data.read(user_data_length)
        yield Packet(
            primary_header = primary_header,
            secondary_header = secondary_header,
            user_data_field = user_data
        )


def packet_generator_from_file(filename):
    with open(filename, 'rb') as data:
        return packet_generator(data)


def build_data_word_dict(PacketGenerator, num_packets, log: bool = True, log_interval: int = 10):
    data_word_dicts = []
    sub_comm_dict = SUB_COMM_KEY_VAL.copy()
    
    initial_data_word_index = 0
    sc_data_word_index = 0

    for i in range(num_packets):
        if log and i % log_interval == 0 and i > 0:
            print(f"Decoded {i} of {num_packets}.")

        packet = next(PacketGenerator)

        sc_data_word_index = int(packet.secondary_header['sc_data_word_index'], 2)
        if i == 0:
            initial_data_word_index = sc_data_word_index
        else:
            if sc_data_word_index == initial_data_word_index:
                data_word_dicts.append(sub_comm_dict)
                sub_comm_dict = SUB_COMM_KEY_VAL.copy()

        key, pos = SUB_COMM_KEY_POS[sc_data_word_index]
        pos = pos * WORD_SIZE
        sub_comm_dict[key] = sub_comm_dict[key][0:pos] + packet.secondary_header['sc_data_word'] + sub_comm_dict[key][pos+WORD_SIZE:]
    
    if sc_data_word_index != initial_data_word_index:
        data_word_dicts.append(sub_comm_dict)

    return data_word_dicts