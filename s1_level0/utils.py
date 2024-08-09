"""
By: Andrew Player
Description: Some basic utility functions necessary for decoding Level-0 data.
             For more context, see "SAR Space Packet Protocol Data Unit" at:
             https://sentinels.copernicus.eu/documents/247904/2142675/Sentinel-1-SAR-Space-Packet-Protocol-Data-Unit.pdf
"""

from structs import BRC_TO_HUFFMAN_START_BIT_LEN, BRC_TO_HUFFMAN_CODING


def create_bit_string(bytes_string: str):
    bit_string = ''
    for byte in bytes_string:
        bit_string += '{:08b}'.format(byte)
    return bit_string


def read_and_pop(bit_string: str, bit_length: int):
    return bit_string[0:bit_length], bit_string[bit_length:]


def huffman_decode(bit_string, start_bit_len, bit_pattern_to_code):
    bits = ''
    bit_len = start_bit_len
    temp_bit_string = ''
    while bits not in bit_pattern_to_code:
        bits, temp_bit_string = read_and_pop(bit_string, bit_len)
        if bits not in bit_pattern_to_code:
            bit_len += 1
        if bit_len > 10:
            raise ValueError(f"Huffman pattern matching exceeded max length. Bits: {bits}, Pattern: {bit_pattern_to_code}")
    return bit_pattern_to_code[bits], temp_bit_string, bit_len


def huffman_decode_for_brc(bit_string: str, brc: int):
    return huffman_decode(
        bit_string,
        BRC_TO_HUFFMAN_START_BIT_LEN[brc],
        BRC_TO_HUFFMAN_CODING[brc]
    )
