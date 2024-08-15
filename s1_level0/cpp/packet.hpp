#pragma once

#include <iostream>
#include <unordered_map>
#include <complex>

#include "structs.hpp"

using namespace std;


struct H_CODE {
    vector<u_int8_t> signs;
    vector<u_int16_t> m_codes;

    int bits_read;
};


struct QUAD {
    vector<vector<u_int8_t>> signs;
    vector<vector<u_int16_t>> m_codes;

    string key;

    int bits_read;

    QUAD(const string& component_key) {
        key = component_key;
    }
};


class L0Packet 
{
private:
    unordered_map<string, int> _primary_header;
    unordered_map<string, int> _secondary_header;

    vector<u_int8_t> _raw_user_data;

    int _num_quads;
    int _test_mode;
    int _baq_mode;
    int _num_baq_blocks;
    int _user_data_length;
    
    int _bit_index;

    char _data_format;

    vector<int> _brc;
    vector<int> _thresholds;

    vector<complex<double>> _complex_samples;

    bool _complex_samples_set_flag = false;

    void _set_data_format();

    int _get_next_word_boundary(const int& bit_index);
    
    double _get_type_d_s_value(const int& brc, const int& threshold_index, const int& sign, const int& m_code);
    
    H_CODE _get_h_code(const u_int16_t& brc, int& bit_index, const bool& is_last_block);

    vector<complex<double>> _get_type_d_complex_samples(QUAD& IE, QUAD& IO, QUAD& QE, QUAD& QO);
    
    vector<complex<double>> _decode_types_a_and_b();
    
    vector<complex<double>> _decode_type_d();
    
    vector<complex<double>> _decode();

    int _set_quad(QUAD& component, int& bit_index);
    
    void _set_complex_samples();


public:
    L0Packet(
        unordered_map<string, int> primary_header,
        unordered_map<string, int> secondary_header,
        vector<u_int8_t> raw_user_data
    ) {
        _primary_header   = primary_header;
        _secondary_header = secondary_header;
        _raw_user_data    = raw_user_data;

        _num_quads        = secondary_header["num_quadratures"];
        _test_mode        = secondary_header["test_mode"];
        _baq_mode         = secondary_header["baq_mode"];
        _user_data_length = primary_header["packet_data_length"] + 1 - SECONDARY_HEADER_SIZE;
        _num_baq_blocks   = ceil((2.0 * double(_num_quads)) / 256.0);

        if (_user_data_length != _raw_user_data.size()) 
        {
            cout << _user_data_length << " != " << _raw_user_data.size() << endl;
            throw runtime_error("The lenght of the user data field is invalid.");
        }

        _set_data_format();
    }

    int  get_num_quads() {return _num_quads;}
    int  get_test_mode() {return _test_mode;}
    int  get_baq_mode () {return _baq_mode;}
    int  get_num_baq_blocks  () {return _num_baq_blocks;}
    int  get_user_data_length() {return _user_data_length;}
    char get_data_format() {return _data_format;}


    vector<complex<double>> get_complex_samples();

    void print_primary_header();

    void print_secondary_header();
};
