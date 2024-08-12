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
from utils import create_bit_string

# TODO: Implement use of the annot.dat file to grab the locations of each packet
#       so that packet processing can be parallelized.

def get_header_dict(header_bytes, header_bit_lengths, header_field_names):
    read_and_pop = lambda bit_string, bit_length: (bit_string[0:bit_length], bit_string[bit_length:])
    bit_string = create_bit_string(header_bytes)
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


def build_data_word_dict(packet_generator, num_packets: int = 100, log: bool = True, log_interval: int = 10):
    data_word_dicts = []
    sub_comm_dict = SUB_COMM_KEY_VAL.copy()
    
    initial_data_word_index = 0
    sc_data_word_index = 0

    for i in range(num_packets):
        if log and i % log_interval == 0 and i > 0:
            print(f"Decoded {i} of {num_packets}.")

        packet = next(packet_generator)
        secondary_header = packet.get_secondary_header()

        sc_data_word_index = secondary_header['sc_data_word_index']
        if i == 0:
            initial_data_word_index = sc_data_word_index
        else:
            if sc_data_word_index == initial_data_word_index:
                data_word_dicts.append(sub_comm_dict)
                sub_comm_dict = SUB_COMM_KEY_VAL.copy()

        key, pos = SUB_COMM_KEY_POS[sc_data_word_index]
        pos = pos * WORD_SIZE
        data_word =  secondary_header['sc_data_word']
        sub_comm_dict[key] = sub_comm_dict[key][0:pos] + data_word + sub_comm_dict[key][pos+WORD_SIZE:]
    
    if sc_data_word_index != initial_data_word_index:
        data_word_dicts.append(sub_comm_dict)

    return data_word_dicts


def index_decoder(raw_data):
    """
    Block Index: 36 Octets
        Date/Time: 8 Octets (MJD 1950)
        Data Time Delta: 8 Octets (milliseconds)
        Size of Data Unit: 4 Octets
        Data Unit Offset from File Beginning: 4 Octets (1 indexed)
        Bytes Offset from File Beginning: 8 Octets (0 indexed)
        Variable Data Size Flag: 1 Octet
        Spare Data to Align to 36 Bytes: 3 Octets
    """
    index_records = []
    while raw_data:
        data = raw_data.read(36)
        if not data:
            break
        record = {
            'date_time': int.from_bytes(data[0:8], 'big'),
            'time_delta': int.from_bytes(data[8:16], 'big'),
            'data_size': int.from_bytes(data[16:20], 'big'),
            'unit_offset': int.from_bytes(data[20:24], 'big'),
            'byte_offset': int.from_bytes(data[24:32], 'big'),
            'variable_flag': int.from_bytes(data[32:33], 'big'),
            'spare_data': int.from_bytes(data[33:36], 'big'),
        }
        index_records.append(record)
    return index_records


def annotation_decoder(raw_data):
    """
    Annotation Record: 26 Octets
        Aquisition Time: 2 Octets (utc time, days since Jan 1. 2000)
        Aquisition Time: 4 Octets (utc time, milliseconds since beginning of day)
        Aquisition Time: 2 Octets (utc time, microseconds since the last millisecond)
        Packet Length: 2 Octets
        Number of Transfer Frames: 2 Octets
        CRC Error Flag: 1 Octet
        Bit Type: 1 Bit
        Bit 2 Type: 2 Bits (2-bit bit mask)
        Bit 6 Type: 6 Bits (6-bit bit mask)
        Spare Field: 1 Octet
    """
    annotation_records = []
    while raw_data:
        data = raw_data.read(26)
        if not data:
            break
        bit_string = create_bit_string(data)
        record = {
            'days_ul': int(bit_string[0:16], 2),
            'milliseconds_ul': int(bit_string[16:48], 2),
            'microseconds_ul': int(bit_string[48:64], 2),
            'days_dl': int(bit_string[64:80], 2),
            'milliseconds_dl': int(bit_string[80:112], 2),
            'microseconds_dl': int(bit_string[112:128], 2),
            'packet_length': int(bit_string[128:144], 2),
            'num_transfer_frames': int(bit_string[144:160], 2),
            'error_flag': int(bit_string[160:168], 2),
            'bit_1_type': int(bit_string[168:169], 2),
            'bit_2_type': int(bit_string[169:171], 2),
            'bit_6_type': int(bit_string[171:177], 2),
            'spare_field': int(bit_string[177:185], 2)
        }
        annotation_records.append(record)
    return annotation_records