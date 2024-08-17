#include "packet.hpp"


int L0Packet::get_baq_block_length()
{
    return 8 * (_secondary_header["baq_block_length"] + 1);
}


double L0Packet::get_pri()
{
    return _secondary_header["pri"] / F_REF;
}


double L0Packet::get_pulse_length()
{
    return _secondary_header["pulse_length"] / F_REF;
}


double L0Packet::get_swl()
{
    return _secondary_header["swl"] / F_REF;
}


double L0Packet::get_swst()
{
    return _secondary_header["swst"] / F_REF;
}


double L0Packet::get_rx_gain()
{
    return -0.5 * _secondary_header["rx_gain"];
}


double L0Packet::get_start_frequency()
{
    int sign = _secondary_header["pulse_start_frequency_sign"] == 0 ? -1 : 1;
    int mag  = _secondary_header["pulse_start_frequency_mag"];

    double txprr = get_tx_ramp_rate();

    return (sign * mag * (F_REF / 16384)) + (txprr / (4 * F_REF));
}


double L0Packet::get_tx_ramp_rate()
{
    int sign = _secondary_header["tx_ramp_rate_sign"] == 0 ? -1 : 1;
    int mag  = _secondary_header["tx_ramp_rate_mag"];

    return sign * mag * (pow(F_REF, 2) / 2097152);
}


char L0Packet::get_tx_polarization()
{
    int pol_code = _secondary_header["polarisation"];
    
    if (pol_code >= 0 && pol_code <= 3)
    {
        return 'H';
    }
    else if (pol_code >= 4 && pol_code <= 7)
    {
        return 'V';
    }
    else
    {
        throw runtime_error("The polarization code is invalid.");
    }
}


char L0Packet::get_rx_polarization()
{
    switch (_secondary_header["rx_channel_id"])
    {
        case 0:
            return 'V';
        case 1:
            return 'H';
        default:
            throw runtime_error("The rx_channel_id is invalid.");
    }
}


string L0Packet::get_baq_mode()
{
    string baq_mode = unordered_map<int, string>({
        {0,  "bypass_mode"},
        {3,  "3_bit_mode"},
        {4,  "4_bit_mode"},
        {5,  "5_bit_mode"},
        {12, "fdbaq_mode_0"},
        {13, "fdbaq_mode_1"},
        {14, "fdbaq_mode_2"}
    })[_baq_mode];
    
    return baq_mode == "" ? "n_a" : baq_mode;
}


string L0Packet::get_test_mode()
{
    string test_mode = unordered_map<int, string>({
        {0, "measurement_mode"},
        {1, "n_a"},
        {3, "n_a"},
        {4, "contingency"},
        {5, "contingency"},
        {6, "test_mode_baq"},
        {7, "test_mode_bypass"}
    })[_test_mode];

    if (test_mode == "")
    {
        throw out_of_range("The test mode number is not in the range of valid values.");
    }
    return test_mode;
}


string L0Packet::get_sensor_mode()
{
    return ECC_CODE_TO_SENSOR_MODE[_secondary_header["ecc_number"]];
}


string L0Packet::get_signal_type()
{
    string signal_type = unordered_map<int, string>({
        {0,  "echo"},
        {1,  "noise"},
        {8,  "tx_cal"},
        {9,  "rx_cal"},
        {10, "epdn_cal"},
        {11, "ta_cal"},
        {12, "apdn_cal"},
        {15, "txh_cal_iso"}
    })[_secondary_header["signal_type"]];
    
    return signal_type == "" ? "n_a" : signal_type;
}


string L0Packet::get_error_status()
{
    return _secondary_header["error_flag"] == 0 ? "nominal" : "ssb_corrupt";
}


void L0Packet::print_primary_header() 
{
    for (string key : PRIMARY_HEADER_FIELDS) 
    {
        cout << key << ": " << _primary_header[key] << endl;
    }
}


void L0Packet::print_secondary_header() 
{
    for (string key : SECONDARY_HEADER_FIELDS) 
    {
        if (key.substr(0, 3) == "na_")
        {
            continue;
        }
        cout << key << ": " << _secondary_header[key] << endl;
    }
}


void L0Packet::print_modes()
{
    cout << "BAQ Mode: " << get_baq_mode() << endl;
    cout << "BAQ Block Length: " << get_baq_block_length() << endl;
    cout << "Test Mode: " << get_test_mode() << endl;
    cout << "Sensor Mode: " << get_sensor_mode() << endl;
    cout << "Signal Type: " << get_signal_type() << endl;
    cout << "Error Status: " << get_error_status() << endl;
}


void L0Packet::print_pulse_info() 
{
    cout << "RX Polarization: " << get_rx_polarization() << endl;
    cout << "TX Polarization: " << get_tx_polarization() << endl;
    cout << "Pulse Length: " << get_pulse_length() << endl;
    cout << "TX Ramp Rate (TXPRR): " << get_tx_ramp_rate() << endl;
    cout << "Start Frequency (TXPSF): " << get_start_frequency() << endl;
    cout << "PRI: " << get_pri() << endl;
    cout << "SWL: " << get_swl() << endl;
    cout << "SWST: " << get_swst() << endl;
    cout << "RX Gain: " << get_rx_gain() << endl;
    cout << "Range Decimation: " << _secondary_header["range_decimation"] << endl;
    cout << "TX Pulse Number: " << _secondary_header["tx_pulse_number"] << endl;
}


void L0Packet::_set_data_format() 
{
    unordered_set<int> type_c_modes = { 3,  4,  5};
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


/***********************************************************************/

/* DECODING COMPLEX SAMPLES                                            */

/***********************************************************************/


vector<complex<double>> L0Packet::get_complex_samples()
{
    if (!_complex_samples_set_flag)
    {
        _set_complex_samples();
    }
    return _complex_samples;
}


void L0Packet::_decode() 
{
    if (_data_format == 'A' || _data_format == 'B') 
    {
        _complex_samples =  _decode_types_a_and_b();
    }
    else if (_data_format == 'C') 
    {
        throw runtime_error("Packet is Type C. Decoding is not supported.");
    }
    else 
    {
        _complex_samples = _decode_type_d();
    }
}


void L0Packet::_set_complex_samples()
{
    _decode();
    _complex_samples_set_flag = true;

    // swapping _raw_user_data with a blank vector to free memory
    vector<u_int8_t>().swap(_raw_user_data);
}


int L0Packet::_get_next_word_boundary(const int& bit_index)
{
    int offset = bit_index % WORD_SIZE;
    if (offset == 0) return bit_index;
    return bit_index + (WORD_SIZE - offset);
}


/***********************************************************************/

/* TYPE D PACKETS                                                      */

/***********************************************************************/


double L0Packet::_get_type_d_s_value(
    const u_int8_t& brc,
    const u_int16_t& threshold_index,
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

    for (int block_id = 0; block_id < _num_baq_blocks; block_id++)
    {
        bool is_last_block = (block_id == _num_baq_blocks - 1);
        int  block_length  = is_last_block ? _num_quads - (128 * (_num_baq_blocks - 1)) : 128;
        int  brc           = _brc[block_id];
        int  threshold_id  = _thresholds[block_id];

        for (int s_id = 0; s_id < block_length; s_id++)
        {
            s_values.push_back({
                _get_type_d_s_value(brc, threshold_id, IE.signs[block_id][s_id], IE.m_codes[block_id][s_id]),
                _get_type_d_s_value(brc, threshold_id, IO.signs[block_id][s_id], IO.m_codes[block_id][s_id]),
                _get_type_d_s_value(brc, threshold_id, QE.signs[block_id][s_id], QE.m_codes[block_id][s_id]),
                _get_type_d_s_value(brc, threshold_id, QO.signs[block_id][s_id], QO.m_codes[block_id][s_id]),
            });
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


H_CODE L0Packet::_get_h_code(const u_int8_t& brc, int& bit_index, const bool& is_last_block)
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
    u_int8_t brc;
    u_int16_t threshold;

    int brc_bits       = 3;
    int threshold_bits = 8;       

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
                throw runtime_error("BRC value is invalid.");
            }
            _brc.push_back(brc);
            bit_index += brc_bits;
        }
        else if (is_qe)
        {
            threshold = read_n_bits(_raw_user_data, bit_index, threshold_bits);
            if (threshold > 256)
            {
                throw runtime_error("Threshold Index is invalid.");
            }
            _thresholds.push_back(threshold);
            bit_index += threshold_bits;
        }
        brc = _brc[i];

        H_CODE h_code = _get_h_code(brc, bit_index, is_last_block);

        component.signs.push_back(h_code.signs);
        component.m_codes.push_back(h_code.m_codes);

        int brc_offset       = is_ie ? brc_bits       : 0;
        int threshold_offset = is_qe ? threshold_bits : 0;

        component.bits_read += h_code.bits_read + brc_offset + threshold_offset;
    }

    return _get_next_word_boundary(bit_index);
}


vector<complex<double>> L0Packet::_decode_type_d()
{
    QUAD IE = QUAD("IE");
    QUAD IO = QUAD("IO");
    QUAD QE = QUAD("QE");
    QUAD QO = QUAD("QO");

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


/***********************************************************************/

/* TYPE A AND B PACKETS                                                */

/***********************************************************************/


vector<complex<double>> L0Packet::_get_types_a_and_b_complex_samples(
    QUAD& IE,
    QUAD& IO,
    QUAD& QE,
    QUAD& QO
) {
    auto get_s_value = [](u_int8_t sign, u_int16_t m_code) {return pow(-1, sign) * m_code;};

    int num_s_codes = IE.signs[0].size();

    vector<vector<double>> s_values;

    for(int i = 0; i < num_s_codes; i++)
    {
        s_values.push_back({
            get_s_value(IE.signs[0][i], IE.m_codes[0][i]),
            get_s_value(IO.signs[0][i], IO.m_codes[0][i]),
            get_s_value(QE.signs[0][i], QE.m_codes[0][i]),
            get_s_value(QO.signs[0][i], QO.m_codes[0][i])
        });
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


int L0Packet::_set_a_and_b_quad(QUAD& component, int& bit_index)
{
    int num_bits = 0;
    int sign_bits = 1;
    int m_code_bits = 9;

    H_CODE h_code;

    for (int i = 0; i < _num_quads; i++)
    {
        u_int8_t sign   = read_n_bits(_raw_user_data, bit_index, sign_bits);
        bit_index += sign_bits;
        
        u_int16_t m_code = read_n_bits(_raw_user_data, bit_index, m_code_bits);
        bit_index += m_code_bits;

        h_code.signs.push_back(sign);
        h_code.m_codes.push_back(m_code);
    }

    component.signs.push_back(h_code.signs);
    component.m_codes.push_back(h_code.m_codes);

    return _get_next_word_boundary(bit_index);
}


vector<complex<double>> L0Packet::_decode_types_a_and_b()
{
    QUAD IE = QUAD("IE");
    QUAD IO = QUAD("IO");
    QUAD QE = QUAD("QE");
    QUAD QO = QUAD("QO");

    int bit_index = 0;

    bit_index = _set_a_and_b_quad(IE, bit_index);
    bit_index = _set_a_and_b_quad(IO, bit_index);
    bit_index = _set_a_and_b_quad(QE, bit_index);
    bit_index = _set_a_and_b_quad(QO, bit_index);

    vector<complex<double>> complex_samples = _get_types_a_and_b_complex_samples(
        IE,
        IO,
        QE,
        QO
    );

    return complex_samples;
}