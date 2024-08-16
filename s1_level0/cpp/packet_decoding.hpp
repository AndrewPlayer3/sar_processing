#pragma once

#include "packet.hpp"

unordered_map<string, int> get_header_dict(
    const vector<u_int8_t>& bytes,
    const vector<int>&      bit_lengths,
    const vector<string>&   field_names
);

L0Packet decode_next_packet(ifstream& data);

vector<L0Packet> get_all_packets(ifstream& data, const bool& log, const int& log_interval);

vector<L0Packet> get_n_packets(ifstream& data, const int& n, const bool& log, const int& log_interval);

vector<unordered_map<string, int>> annotation_decoder(ifstream& data);

vector<unordered_map<string, int>> index_decoder(ifstream& data);

double time_packet_generation(ifstream& data, const int& num_packets, const bool& log, const int& log_interval);