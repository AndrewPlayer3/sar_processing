#include "packet.hpp"


vector<complex<double>> L0Packet::get_complex_samples()
{
    if (!_complex_samples_set_flag)
    {
        _set_complex_samples();
    }
    return _complex_samples;
}


void L0Packet::print_primary_header() 
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

void L0Packet::print_secondary_header() 
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


void L0Packet::_set_data_format() 
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


int L0Packet::_get_next_word_boundary(const int& bit_index)
{
    int offset = bit_index % WORD_SIZE;
    if (offset == 0) return 0;
    else return bit_index + (WORD_SIZE - offset);
}


vector<complex<double>> L0Packet::_decode_types_a_and_b() 
{
    vector<complex<double>> complex_samples;
    return complex_samples;
}


double L0Packet::_get_type_d_s_value(
    const int& brc,
    const int& threshold_index,
    const int& sign,
    const int& m_code
) {
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


vector<complex<double>> L0Packet::_get_type_d_complex_samples(
    QUAD& IE,
    QUAD& IO,
    QUAD& QE,
    QUAD& QO
) {
    vector<vector<double>> s_values;

    for (int block_index = 0; block_index < _num_baq_blocks; block_index++)
    {
        bool is_last_block   = (block_index == _num_baq_blocks - 1);
        int  block_length    = is_last_block ? _num_quads - (128 * (_num_baq_blocks - 1)) : 128;
        int  brc             = _brc[block_index];
        int  threshold_index = _thresholds[block_index];

        for (int s_code_index = 0; s_code_index < block_length; s_code_index++)
        {
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
    vector<complex<double>> complex_samples;

    for (int i = 1; i <= _num_quads; i++)
    {
        vector<double> components = s_values[i-1];

        complex_samples.push_back(complex<double>(components[0], components[2]));
        complex_samples.push_back(complex<double>(components[1], components[3]));
    }

    return complex_samples;
}


H_CODE L0Packet::_get_h_code(const u_int16_t& brc, int& bit_index, const bool& is_last_block)
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


int L0Packet::_set_quad(QUAD& component, int& bit_index)
{   
    u_int16_t brc;
    u_int8_t  threshold;

    int brc_bits       = 3;
    int threshold_bits = 8;

    int total_bits_read    = 0;
    int bits_read_for_code = 0;       

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


vector<complex<double>> L0Packet::_decode_type_d()
{
    QUAD IE = QUAD("IE");
    QUAD IO = QUAD("IO");
    QUAD QE = QUAD("QE");
    QUAD QO = QUAD("QO");

    int bit_counts[4];
    int bit_index = 0;

    bit_index = _set_quad(IE, bit_index);
    bit_index = _set_quad(IO, bit_index);
    bit_index = _set_quad(QE, bit_index);
    bit_index = _set_quad(QO, bit_index);

    vector<complex<double>> complex_samples = _get_type_d_complex_samples(
        IE,
        IO,
        QE,
        QO
    );

    return complex_samples;
}


vector<complex<double>>L0Packet:: _decode() 
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


void L0Packet::_set_complex_samples()
{
    _complex_samples = _decode();
    _complex_samples_set_flag = true;

    // swapping _raw_user_data with a blank vector to free memory
    vector<u_int8_t>().swap(_raw_user_data);
}