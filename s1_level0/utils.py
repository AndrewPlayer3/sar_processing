"""
By: Andrew Player
Description: Some basic utility functions necessary for decoding Level-0 data.
             For more context, see "SAR Space Packet Protocol Data Unit" at:
             https://sentinels.copernicus.eu/documents/247904/2142675/Sentinel-1-SAR-Space-Packet-Protocol-Data-Unit.pdf
"""

import time

import numpy as np

from structs import BRC_TO_HUFFMAN_START_BIT_LEN, BRC_TO_HUFFMAN_CODING, BRC_TO_HUFFMAN_CODING_SET


def create_bit_string(bytes_string: str):
    bit_string = ''
    for byte in bytes_string:
        bit_string += '{:08b}'.format(byte)
    return bit_string


def read_and_pop(bit_string: str, bit_length: int):
    return bit_string[0:bit_length], bit_string[bit_length:]


def huffman_decode(bit_string, start_bit_len, bit_pattern_set, bit_pattern_to_code):
    bits = None
    bit_len = start_bit_len
    temp_bit_string = ''
    while bits not in bit_pattern_set:
        bits, temp_bit_string = read_and_pop(bit_string, bit_len)
        if bits not in bit_pattern_set:
            bit_len += 1
        if bit_len > 10:
            raise ValueError(f"Huffman pattern matching exceeded max length. Bits: {bits}, Pattern: {bit_pattern_to_code}")
    return bit_pattern_to_code[bits], temp_bit_string, bit_len


def huffman_decode_for_brc(bit_string: str, brc: int):
    return huffman_decode(
        bit_string,
        BRC_TO_HUFFMAN_START_BIT_LEN[brc],
        BRC_TO_HUFFMAN_CODING_SET[brc],
        BRC_TO_HUFFMAN_CODING[brc]
    )


def find_packet_of_type(PacketGenerator, packet_type: str, num_packets: int = 1000, log: bool = True, log_interval: int = 10):
    packet_index = 0
    for i in range(num_packets):
        packet = next(PacketGenerator)
        if i != 0 and log and i % log_interval == 0:
            print(f"Decoded Packet {i} of {num_packets}")
        if packet.data_format() == packet_type:
            packet_index = i
            if log:
                print(f"Packet number {i} is a type {packet_type} packet.")
            break
    return packet, packet_index


def time_packet_generation(PacketGenerator, num_packets, perf_log_interval, log: bool = True):
    times = []
    for i in range(num_packets):
        start_time = time.time()
        _ = next(PacketGenerator)
        end_time = time.time()
        runtime = end_time - start_time
        times.append(runtime)
        if log and i % perf_log_interval == 0:
            print(f"Decoded Packet {i} of {num_packets} in {runtime}s.")
    time_arr = np.asarray(times)
    mean = time_arr.mean()
    total = sum(times)
    if log:
        print("---")
        print(f"Decoded {num_packets} in {total}s.")
        print("___")
        print(f"Mean Decoding Time: {mean}s.")
    return total, mean