#include <iostream>
#include <iomanip>
#include <sstream>
#include <string>
#include <fstream>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <complex>
#include <math.h>

#include "structs.hpp"

using namespace std;


u_int32_t read_n_bits(const std::vector<u_int8_t>& data, int bit_index, int n);
u_int16_t huffman_decode(vector<u_int8_t>& data, int brc, int& bit_index);


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

    QUAD(string component_key) {
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

    char _data_format;

    vector<int> _brc;
    vector<int> _thresholds;

    void _set_data_format() 
    {
        unordered_set<int> type_c_modes = {3, 4, 5};
        unordered_set<int> type_d_modes = {12, 13, 14};

        if (_baq_mode == 0) 
        {
            if (_test_mode % 3 == 0) 
            {
                _data_format = 'A';
            } 
            else 
            {
                _data_format = 'B';
            }
        }
        else if (type_c_modes.contains(_baq_mode)) 
        {
            _data_format = 'C';
        }
        else if (type_d_modes.contains(_baq_mode)) 
        {
            _data_format = 'D';
        }
        else 
        {
            throw out_of_range("BAQ Mode is invalid.");
        }
    }


    int _get_next_word_boundary(int bit_index)
    {
        int offset = bit_index % WORD_SIZE;
        if (offset == 0) return 0;
        else return WORD_SIZE - offset;
    }


    vector<complex<double>> _decode_types_a_and_b() 
    {
        vector<complex<double>> complex_samples;
        return complex_samples;
    }


    double _get_type_d_s_value(
        int brc,
        int threshold_index,
        int sign,
        int m_code
    )
    {
        if (threshold_index <= BRC_TO_THIDX[brc])
        {
            int m_code_comparison_flag = BRC_TO_M_CODE[brc];
            
            if (m_code < m_code_comparison_flag)
            {
                return pow(-1.0, sign) * m_code;
            }
            else if (m_code == m_code_comparison_flag)
            {
                return pow(-1.0, sign) * SIMPLE_RECONSTRUCTION_METHOD[1][brc][threshold_index];
            }
            else
            {
                throw runtime_error("MCode is greater than the comparison flag.");
            }
        }
        return pow(-1.0, sign) * NORMALIZED_RECONSTRUCTION_LEVELS[1][brc][m_code] * THIDX_TO_SF_ARRAY[threshold_index];
    }


    vector<complex<double>> _get_type_d_complex_samples(
        QUAD& IE,
        QUAD& IO,
        QUAD& QE,
        QUAD& QO
    ){
        vector<vector<double>> s_values;
        cout << "DECODING COMPLEX BLOCKS AND SCODES" << endl;
        for (int block_index; block_index < _num_baq_blocks; block_index++)
        {

            cout << "DECODING COMPLEX BLOCK " << block_index << endl;

            bool is_last_block   = (block_index == _num_baq_blocks - 1);
            int  block_length    = is_last_block ? _num_quads - (128 * (_num_baq_blocks - 1)) : 128;
            int  brc             = _brc[block_index];
            int  threshold_index = _thresholds[block_index];

            for (int s_code_index; s_code_index < block_length; s_code_index++)
            {

                cout << "DECODING COMPLEX SVALUE " << s_code_index << endl;

                double ie_s_value = _get_type_d_s_value(
                    brc,
                    threshold_index,
                    IE.signs[block_index][s_code_index],
                    IE.m_codes[block_index][s_code_index]
                );
                double io_s_value = _get_type_d_s_value(
                    brc,
                    threshold_index,
                    IO.signs[block_index][s_code_index],
                    IO.m_codes[block_index][s_code_index]
                );
                double qe_s_value = _get_type_d_s_value(
                    brc,
                    threshold_index,
                    QE.signs[block_index][s_code_index],
                    QE.m_codes[block_index][s_code_index]
                );
                double qo_s_value = _get_type_d_s_value(
                    brc,
                    threshold_index,
                    QO.signs[block_index][s_code_index],
                    QO.m_codes[block_index][s_code_index]
                );
                s_values.push_back(vector<double>({ie_s_value, io_s_value, qe_s_value, qo_s_value}));
            }
        }
        // complex<double> complex_samples[2 * _num_quads];

        vector<complex<double>> complex_samples;

        for (int i = 1; i <= _num_quads; i++)
        {
            vector<double> components = s_values[i-1];
            // complex_samples[(2*i)-2] = complex<double>(components[0], components[2]);
            // complex_samples[(2*i)-1] = complex<double>(components[1], components[3]);
            complex_samples.push_back(complex<double>(components[0], components[2]));
            complex_samples.push_back(complex<double>(components[1], components[3]));
        }

        return complex_samples;
    }


    H_CODE _get_h_code(u_int16_t brc, int& bit_index, bool is_last_block)
    {
            H_CODE h_code;

            int num_codes = is_last_block ? _num_quads - (128 * (_num_baq_blocks - 1)) : 128;
            for (int i = 0; i < num_codes; i++)
            {
                int start_bit_index = bit_index;
                int sign   = read_n_bits(_raw_user_data, bit_index, 1);

                bit_index += 1;

                u_int16_t m_code = huffman_decode(_raw_user_data, brc, bit_index);  // increments bit index

                h_code.signs.push_back(sign);
                h_code.m_codes.push_back(m_code);                

                h_code.bits_read += (bit_index - start_bit_index);
            }

            return h_code;
    }


    int _set_quad(QUAD& component)
    {   
        u_int16_t brc;
        u_int8_t  threshold;

        int brc_bits       = 3;
        int threshold_bits = 8;

        int total_bits_read    = 0;
        int bits_read_for_code = 0;

        int bit_index = 0;        

        for (int i = 0; i < _num_baq_blocks; i++)
        {
            bool is_ie = (component.key == "IE");
            bool is_qe = (component.key == "QE");
            bool is_last_block = (i == _num_baq_blocks - 1);
            if (is_ie)
            {
                brc = read_n_bits(_raw_user_data, bit_index, brc_bits);
                if (brc > 4)
                {
                    throw runtime_error("The BRC value is invalid.");
                }
                _brc.push_back(brc);
                bit_index += brc_bits;
            }
            else if (is_qe)
            {
                threshold = read_n_bits(_raw_user_data, bit_index, threshold_bits);
                _thresholds.push_back(threshold);
                bit_index += threshold_bits;
            }
            brc = _brc[i];

            H_CODE h_code = _get_h_code(brc, bit_index, is_last_block);

            component.signs.push_back(h_code.signs);
            component.m_codes.push_back(h_code.m_codes);

            component.bits_read += h_code.bits_read;

            int brc_offset       = is_ie ? brc_bits       : 0;
            int threshold_offset = is_qe ? threshold_bits : 0;

            total_bits_read += h_code.bits_read + brc_offset + threshold_offset;
        }

        return _get_next_word_boundary(bit_index);
    }


    vector<complex<double>> _decode_type_d()
    {
        QUAD IE = QUAD("IE");
        QUAD IO = QUAD("IO");
        QUAD QE = QUAD("QE");
        QUAD QO = QUAD("QO");

        int bit_counts[4];

        cout << "DECODING IE" << endl;
        bit_counts[0] = _set_quad(IE);
        cout << "DECODING IO" << endl;
        bit_counts[1] = _set_quad(IO);
        cout << "DECODING QE" << endl;
        bit_counts[2] = _set_quad(QE);
        cout << "DECODING QO" << endl;
        bit_counts[3] = _set_quad(QO);

        // for (u_int16_t m_code : IE.m_codes[0])
        // {
        //     cout << int(m_code) << endl;
        // }

        cout << "DECODING COMPLEX SAMPLES" << endl;
        vector<complex<double>> complex_samples = _get_type_d_complex_samples(
            IE,
            IO,
            QE,
            QO
        );

        // vector<unsigned long> complex_values = 
        // {
        //     IE.signs.size(),
        //     IE.m_codes.size(),
        //     IO.signs.size(),
        //     IO.m_codes.size(),
        //     QE.signs.size(),
        //     QE.m_codes.size(),
        //     QO.signs.size(),
        //     QO.m_codes.size()
        // };

        return complex_samples;
    }


    vector<complex<double>> _decode() 
    {
        if (_data_format == 'A' || _data_format == 'B') 
        {
            return _decode_types_a_and_b();
        }
        else if (_data_format == 'C') 
        {
            throw runtime_error("Packet is Type C. Decoding is not supported.");
        }
        else 
        {
            return _decode_type_d();
        }
    }


public:
    L0Packet(
        unordered_map<string, int> primary_header,
        unordered_map<string, int> secondary_header,
        vector<u_int8_t> raw_user_data
    ){
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


    vector<complex<double>> get_complex_samples()
    {
        return _decode();
    }


    void print_primary_header() 
    {
        cout << "---------------" << endl;
        cout << "Primary Header:" << endl;
        cout << "---------------" << endl;
        for (string key : PRIMARY_HEADER_FIELDS) 
        {
            cout << key << ": " << _primary_header[key] << endl;
        }
        cout << "---------------" << endl;
    }

    void print_secondary_header() 
    {
        cout << "-----------------" << endl;
        cout << "Secondary Header:" << endl;
        cout << "-----------------" << endl;
        for (string key : SECONDARY_HEADER_FIELDS) 
        {
            cout << key << ": " << _secondary_header[key] << endl;
        }
        cout << "-----------------" << endl;
    }
};
