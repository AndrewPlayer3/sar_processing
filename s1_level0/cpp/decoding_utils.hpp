#pragma once

#include <chrono>
#include <fstream>
#include <unordered_map>
#include <complex>

#include "structs.hpp"


u_int16_t huffman_decode(const vector<u_int8_t>& data, const int& brc, int& bit_index);

vector<u_int8_t> read_bytes(ifstream&  data, const int& num_bytes);

u_int64_t read_n_bits(const std::vector<u_int8_t>& data, const int& start_bit, const int& n);