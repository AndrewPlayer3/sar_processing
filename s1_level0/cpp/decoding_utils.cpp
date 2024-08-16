#include <iostream>
#include "decoding_utils.hpp"


u_int16_t huffman_decode_with_length(const vector<u_int8_t>& data, const int& brc, int& bit_index)
{
    vector<unordered_map<u_int16_t, u_int8_t>> huffman_coding = HUFFMAN_CODINGS_WITH_LENGTH[brc];

    u_int16_t bits = -1;

    int bit_len = BRC_TO_HUFFMAN_START_BIT_LEN[brc];

    int max_bits = 10;
    for (int i = 0; i < max_bits; i++)
    {
        bits = read_n_bits(data, bit_index, bit_len);

        if (!huffman_coding[bit_len - 1].contains(bits)) bit_len += 1;
        else break;

        if (bit_len > 10) 
        {
            throw out_of_range("Max bit length exceeded in Huffman decoding.");
        }
    }
    bit_index += bit_len;

    return huffman_coding[bit_len - 1][bits];
}


u_int16_t huffman_decode(const vector<u_int8_t>& data, const int& brc, int& bit_index)
{
   unordered_map<u_int16_t, u_int8_t> huffman_coding = HUFFMAN_CODINGS[brc];

    u_int16_t bits = -1;

    int bit_len = BRC_TO_HUFFMAN_START_BIT_LEN[brc];


    if (brc == 4)
    {
        if (read_n_bits(data, bit_index, bit_len) == 0)
        {
            bit_index += 2;
            return 0;
        }
        bit_len += 1;
    }

    int max_bits = 10;
    for (int i = 0; i < max_bits; i++)
    {
        bits = read_n_bits(data, bit_index, bit_len);

        if (!huffman_coding.contains(bits)) bit_len += 1;
        else break;

        if (bit_len > 10) 
        {
            throw out_of_range("Max bit length exceeded in Huffman decoding.");
        }
    }
    bit_index += bit_len;

    return huffman_coding[bits];
}


vector<u_int8_t> read_bytes(ifstream&  data, const int& num_bytes) 
{
    vector<u_int8_t> buffer(num_bytes);

    data.read(reinterpret_cast<char*>(buffer.data()), num_bytes);

    return buffer;
}


u_int64_t read_n_bits(const std::vector<u_int8_t>& data, const int& start_bit, const int& n)
{
    if (n < 1 || n > 64) 
    {
        throw invalid_argument("Invalid number of bits to read. Must be between 1 and 64.");
    }

    int byte_index = start_bit / 8;
    int bit_offset = start_bit % 8;

    if (byte_index >= data.size()) 
    {
        throw out_of_range("Start bit is outside of the data vector.");
    }

    u_int64_t result = 0;
    int bits_read = 0;

    while (bits_read < n) 
    {
        if (byte_index >= data.size()) 
        {
            throw out_of_range("Byte index exceeded data vector size.");
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