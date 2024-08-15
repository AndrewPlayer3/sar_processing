#include "packet_decoding.hpp"

using namespace std;


u_int16_t huffman_decode(const vector<u_int8_t>& data, const int& brc, int& bit_index)
{
    unordered_map<u_int16_t, u_int8_t> huffman_coding = BRC_TO_HUFFMAN_CODING[brc];

    int bit_len = BRC_TO_HUFFMAN_START_BIT_LEN[brc];
    int bits    = -1;

    while (!huffman_coding.contains(bits))
    {
        bits = read_n_bits(data, bit_index, bit_len);

        if (!huffman_coding.contains(bits)) 
        {
            bit_len += 1;
        }

        if (bit_len > 10) 
        {
            throw runtime_error("Max bit length exceeded in Huffman decoding.");
        }
    }

    bit_index += bit_len;

    return huffman_coding[bits];
}


vector<u_int8_t> read_bytes(
    ifstream&  data,
    const int& num_bytes
) {
    vector<u_int8_t> buffer(num_bytes);

    data.read(reinterpret_cast<char*>(buffer.data()), num_bytes);

    return buffer;
}


u_int32_t read_n_bits(
    const std::vector<u_int8_t>& data,
    const int& start_bit, 
    const int& n
) {
    if (n < 1 || n > 32) 
    {
        throw invalid_argument("Invalid number of bits to read. Must be between 1 and 32.");
    }

    int byte_index = start_bit / 8;
    int bit_offset = start_bit % 8;

    if (byte_index >= data.size()) 
    {
        throw out_of_range("Start bit is beyond the size of the data vector.");
    }

    u_int32_t result = 0;
    int bits_read = 0;

    while (bits_read < n) 
    {
        if (byte_index >= data.size()) 
        {
            throw out_of_range("Not enough bits available in the data vector.");
        }

        int bits_left_in_byte = 8 - bit_offset;
        int bits_to_read = std::min(bits_left_in_byte, n - bits_read);

        u_int8_t mask = (1 << bits_to_read) - 1;
        u_int8_t shifted_data = (data[byte_index] >> (bits_left_in_byte - bits_to_read)) & mask;

        result = (result << bits_to_read) | shifted_data;

        bits_read += bits_to_read;
        bit_offset = 0;
        byte_index++;
    }

    return result;
}


unordered_map<string, int> get_header_dict(
    const vector<u_int8_t>&  bytes,
    const vector<int>&       bit_lengths,
    const vector<string>&    field_names
) {
    int num_fields = bit_lengths.size();
    int bit_index = 0;

    unordered_map<string, int> header;

    for (int i = 0; i < num_fields; i++) 
    {
        u_int8_t bit_len    = bit_lengths[i];
        string   field_name = field_names[i];

        u_int32_t value = read_n_bits(bytes, bit_index, bit_len);

        header[field_name] = value;

        bit_index += bit_len;
    }
    return header;
}


L0Packet get_next_packet(
    ifstream& data
) {
    vector<u_int8_t> primary_bytes = read_bytes(data, 6);
    unordered_map<string, int> primary_header = get_header_dict(
        primary_bytes,
        PRIMARY_HEADER,
        PRIMARY_HEADER_FIELDS
    );

    vector<u_int8_t> secondary_bytes = read_bytes(data, 62);
    unordered_map<string, int> secondary_header = get_header_dict(
        secondary_bytes,
        SECONDARY_HEADER,
        SECONDARY_HEADER_FIELDS
    );

    u_int32_t packet_length    = primary_header["packet_data_length"];
    u_int32_t user_data_length = packet_length + 1 - SECONDARY_HEADER_SIZE;
    
    vector<u_int8_t> user_data = read_bytes(data, user_data_length);

    L0Packet packet = L0Packet(
        primary_header,
        secondary_header,
        user_data
    );

    return packet;
}