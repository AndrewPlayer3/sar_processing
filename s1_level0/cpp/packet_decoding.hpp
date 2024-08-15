#pragma once

#include <fstream>

#include "packet.hpp"

u_int16_t huffman_decode(const vector<u_int8_t>& data, const int& brc, int& bit_index);

vector<u_int8_t> read_bytes(ifstream& data, const int& num_bytes);

u_int32_t read_n_bits(const std::vector<u_int8_t>& data, const int& start_bit, const int& n);

unordered_map<string, int> get_header_dict(
    const vector<u_int8_t>& bytes,
    const vector<int>&      bit_lengths,
    const vector<string>&   field_names
);

L0Packet get_next_packet(ifstream& data);

