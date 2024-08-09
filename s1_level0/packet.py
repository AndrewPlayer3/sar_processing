import numpy as np

from structs import (
    BRC_TO_HUFFMAN_START_BIT_LEN, 
    BRC_TO_HUFFMAN_CODING,
    SECONDARY_HEADER_SIZE,
    WORD_SIZE,
    SIMPLE_RECONSTRUCTION_METHOD,
    NORMALIZED_RECONSTRUCTION_LEVELS,
    THIDX_TO_SF_ARRAY,
    BRC_TO_THIDX,
    BRC_TO_M_CODE
)

from utils import (
    create_bit_string,
    read_and_pop,
    huffman_decode
)


class Packet:
    def __init__(
        self,
        primary_header,
        secondary_header,
        user_data_field
    ):
        self.__primary_header   = primary_header
        self.__secondary_header = secondary_header

        self.__num_quads      = int(secondary_header['num_quadratures'], 2)
        self.__test_mode      = int(secondary_header['test_mode'], 2)
        self.__baq_mode       = int(secondary_header['baq_mode'], 2)
        self.__num_baq_blocks = int(np.ceil(2 * self.__num_quads / 256))

        self.__user_data_length = (int(primary_header['packet_data_length'], 2) + 1) - SECONDARY_HEADER_SIZE
        self.__raw_user_data = user_data_field

        self.__set_data_format()
        self.__decode_user_data_field()


    def num_quads(self):
        return self.__num_quads


    def num_baq_blocks(self):
        return self.__num_baq_blocks


    def test_mode(self):
        return self.__test_mode


    def baq_mode(self):
        return self.__baq_mode

    
    def user_data_length(self):
        return self.__user_data_length


    def data_format(self):
        return self.__data_format


    def primary_header(self):
        # TODO: Return primary header with proper data types.
        raise NotImplementedError()
    

    def secondary_header(self):
        # TODO: Return secondary header with proper data types.
        raise NotImplementedError()


    def sensor_mode(self):
        # TODO: Map ECC code to the operating mode as per the docs
        raise NotImplementedError()


    def __jump_to_next_word_boundary(self, bit_string, num_bits):
        offset = num_bits % WORD_SIZE
        if offset == 0:
            return bit_string, offset
        next_word_boundary = WORD_SIZE - offset
        _, bit_string = read_and_pop(bit_string, next_word_boundary)
        return bit_string, next_word_boundary


    def __get_type_d_signs_and_m_codes(
        self,
        bit_string: str,
        brc: int,
        last_block: bool
    ) -> tuple[list[int], list[int], str]:
        signs = []
        m_codes = []
        total_bits = 0
        num_s_codes = 128 if not last_block else self.__num_quads - (128 * (self.__num_baq_blocks - 1))
        for _ in range(num_s_codes):
            sign, bit_string = read_and_pop(bit_string, 1)
            m_code, bit_string, bit_len = huffman_decode(
                bit_string,
                BRC_TO_HUFFMAN_START_BIT_LEN[brc],
                BRC_TO_HUFFMAN_CODING[brc]
            )
            signs.append(int(sign, 2))
            m_codes.append(m_code)
            total_bits += (bit_len + 1)
        return signs, m_codes, bit_string, total_bits


    def __type_d_decoder(self, bit_string, component: str):
        brc_size = 3
        threshold_size = 8
        num_bits = 0
        total_bits = 0
        comp_dict = {
            'IE': (self.ie_signs, self.ie_m_codes),
            'IO': (self.io_signs, self.io_m_codes),
            'QE': (self.qe_signs, self.qe_m_codes),
            'QO': (self.qo_signs, self.qo_m_codes)
        }
        comp_signs, comp_m_codes = comp_dict[component]
        for i in range(self.__num_baq_blocks):
            if component == 'IE':
                brc, bit_string = read_and_pop(bit_string, brc_size)
                brc = int(brc, 2)
                if brc > 4:
                    raise ValueError(f'Invalid BRC: {brc} at {i}')
                self.brc.append(brc)
            if component == 'QE':
                threshold, bit_string = read_and_pop(bit_string, threshold_size)
                self.thresholds.append([int(threshold, 2)])
            brc = self.brc[i]
            last_block = i == self.__num_baq_blocks - 1
            signs, m_codes, bit_string, num_bits = self.__get_type_d_signs_and_m_codes(
                bit_string,
                self.brc[i],
                last_block
            )
            comp_signs.append(signs)
            comp_m_codes.append(m_codes)
            brc_offset = brc_size if component == 'IE' else 0
            threshold_offset = threshold_size if component == 'QE' else 0
            total_bits += num_bits + brc_offset + threshold_offset
        bit_string, offset = self.__jump_to_next_word_boundary(bit_string, total_bits)
        return bit_string, total_bits + offset


    def __get_type_d_s_value(self, brc, threshold_index, m_code, sign):
        thidx_comp_flag = BRC_TO_THIDX[brc]
        m_code_comp_flag = BRC_TO_M_CODE[brc]
        if threshold_index <= thidx_comp_flag:
            if m_code < m_code_comp_flag:
                return (-1 ** sign) * m_code
            elif m_code == m_code_comp_flag:
                simple_recon = SIMPLE_RECONSTRUCTION_METHOD[1][brc][threshold_index]
                return ((-1) ** sign) * simple_recon
            else:
                raise ValueError(f'm_code not valid: {m_code}')
        elif threshold_index > thidx_comp_flag:
            normal_recon = NORMALIZED_RECONSTRUCTION_LEVELS[1][brc][m_code]
            sigma_factor = THIDX_TO_SF_ARRAY[threshold_index]
            return (-1 ** sign) * normal_recon * sigma_factor


    def __type_d_s_value_reconstruction(self):
        self.s_values = []
        for block_id in range(self.__num_baq_blocks):
            brc = self.brc[block_id]
            threshold_index = self.thresholds[block_id][0]
            block_len = len(self.ie_m_codes[block_id])
            for s_code_id in range(block_len):
                ie_s_value = self.__get_type_d_s_value(brc, threshold_index, self.ie_m_codes[block_id][s_code_id], self.ie_signs[block_id][s_code_id])
                io_s_value = self.__get_type_d_s_value(brc, threshold_index, self.io_m_codes[block_id][s_code_id], self.io_signs[block_id][s_code_id])
                qe_s_value = self.__get_type_d_s_value(brc, threshold_index, self.qe_m_codes[block_id][s_code_id], self.qe_signs[block_id][s_code_id])
                qo_s_value = self.__get_type_d_s_value(brc, threshold_index, self.qo_m_codes[block_id][s_code_id], self.qo_signs[block_id][s_code_id])
                component_s_values = [ie_s_value, io_s_value, qe_s_value, qo_s_value]
                self.s_values.append(component_s_values)
        complex_s_value = np.zeros((2 * self.__num_quads, ), dtype=complex)
        for i in range(1, self.__num_quads+1):
            ie, io, qe, qo = tuple(self.s_values[i-1])
            complex_s_value[2*i-2] = ie + 1j*qe
            complex_s_value[2*i-1] = io + 1j*qo
        self.complex_s_values = complex_s_value


    def __decode_type_d_data(self):
        self.brc        = []
        self.thresholds = []
        self.ie_signs, self.ie_m_codes  = [], []
        self.io_signs, self.io_m_codes  = [], []
        self.qe_signs, self.qe_m_codes  = [], []
        self.qo_signs, self.qo_m_codes  = [], []
        bit_string = create_bit_string(self.__raw_user_data)
        bit_string, self.num_ie_bits = self.__type_d_decoder(bit_string, 'IE')
        bit_string, self.num_io_bits = self.__type_d_decoder(bit_string, 'IO')
        bit_string, self.num_qe_bits = self.__type_d_decoder(bit_string, 'QE')
        bit_string, self.num_qo_bits = self.__type_d_decoder(bit_string, 'QO')
        self.remaining_user_data_bits = len(bit_string)
        self.__type_d_s_value_reconstruction()
        self.__raw_user_data = None
        del self.__raw_user_data


    def __decode_user_data_field(self):
        try:
            if self.__data_format == 'A':
                raise NotImplementedError("Data Format A is not supported yet...")
            elif self.__data_format == 'B':
                raise NotImplementedError("Data Format B is not supported yet...")
            elif self.__data_format == 'C':
                raise NotImplementedError("Data Format C is not supported yet...")
            elif self.__data_format == 'D':
                self.__decode_type_d_data()
            else:
                raise ValueError('Packet does not have a valid data format.')
        except Exception as e:
            print(f"Error encountered with data format, skipping user data decoding: {e}")


    def __set_data_format(self):
        if self.__baq_mode == 0:
            if self.__test_mode % 3 == 0:
                self.__data_format = 'A'
            else:
                self.__data_format = 'B'
        elif self.__baq_mode in [3, 4, 5]:
            self.__data_format = 'C'
        elif self.__baq_mode in [12, 13, 14]:
            self.__data_format = 'D'
        else:
            raise ValueError(f'No Data Format with BAQ Mode: {self.__baq_mode} and Test Mode: {self.__test_mode}')


    def __repr__(self):
        return (
            f"Packet Type: {self.__data_format}\n" +
            "--------------\n\n" +

            "Primary Header:\n" +
            "---------------\n" +
            f"Packet Version Number: {int(self.__primary_header['packet_version_number'], 2)}\n" +
            f"Packet Type: {int(self.__primary_header['packet_type'], 2)}\n" +
            f"Secondary Header Flag: {int(self.__primary_header['secondary_header_flag'], 2)}\n" +
            f"Process ID: {int(self.__primary_header['process_id'], 2)}\n" +
            f"Process Category: {int(self.__primary_header['process_category'], 2)}\n" +
            f"Packet Sequence Count: {int(self.__primary_header['packet_sequence_count'], 2)}\n" +
            f"Packet Data Length: {int(self.__primary_header['packet_data_length'], 2)}\n\n" +

            f"Secondary Header:\n" +
            "-----------------\n" +
            f"Coarse Time: {int(self.__secondary_header['coarse_time'], 2)}\n" +
            f"Fine Time: {int(self.__secondary_header['fine_time'], 2)}\n" +
            f"Sync Marker: {int(self.__secondary_header['sync_marker'], 2)}\n" +
            f"Data Take ID: {int(self.__secondary_header['data_take_id'], 2)}\n" +
            f"ECC Code: {int(self.__secondary_header['ecc_number'], 2)}\n" +
            f"Test Mode: {int(self.__secondary_header['test_mode'], 2)}\n" +
            f"RX Channel ID: {int(self.__secondary_header['rx_channel_id'], 2)}\n" +
            f"Instrument Configuration ID: {int(self.__secondary_header['instrument_configuration_id'], 2)}\n" +
            f"Sub-Commutative Word Index: {int(self.__secondary_header['sc_data_word_index'], 2)}\n" +
            f"Sub-Commutative Word: {self.__secondary_header['sc_data_word']}\n" +
            f"Counter Service: {int(self.__secondary_header['counter_service'], 2)}\n" +
            f"PRI Count: {int(self.__secondary_header['pri_count'], 2)}\n" +
            f"Error Flag: {int(self.__secondary_header['error_flag'], 2)}\n" +
            f"BAQ Mode: {int(self.__secondary_header['baq_mode'], 2)}\n" +
            f"BAQ Block Length: {int(self.__secondary_header['baq_block_length'], 2)}\n" +
            f"Range Decimation: {int(self.__secondary_header['range_decimation'], 2)}\n" +
            f"RX Gain: {int(self.__secondary_header['rx_gain'], 2)}\n" +
            f"TX Ramp Rate: {int(self.__secondary_header['tx_ramp_rate'], 2)}\n" +
            f"Pulse Start Frequency: {int(self.__secondary_header['pulse_start_frequency'], 2)}\n" +
            f"Pulse Length: {int(self.__secondary_header['pulse_length'], 2)}\n" +
            f"Rank: {int(self.__secondary_header['rank'], 2)}\n" +
            f"PRI: {int(self.__secondary_header['pri'], 2)}\n" +
            f"SWST: {int(self.__secondary_header['swst'], 2)}\n" +
            f"SWL: {int(self.__secondary_header['swl'], 2)}\n" +
            f"SSB Flag: {int(self.__secondary_header['ssb_flag'], 2)}\n" +
            f"Polarisation: {int(self.__secondary_header['polarisation'], 2)}\n" +
            f"Temperature Compensation: {int(self.__secondary_header['temperature_compensation'], 2)}\n" +
            f"Elevation Beam Address: {int(self.__secondary_header['elevation_beam_address'], 2)}\n" +
            f"Azimuth Beam Address: {int(self.__secondary_header['azimuth_beam_address'], 2)}\n" +
            f"Calibration Mode: {int(self.__secondary_header['calibration_mode'], 2)}\n" +
            f"TX Pulse Number: {int(self.__secondary_header['tx_pulse_number'], 2)}\n" +
            f"Signal Type: {int(self.__secondary_header['signal_type'], 2)}\n" +
            f"Swap: {int(self.__secondary_header['swap'], 2)}\n" +
            f"Swath Number: {int(self.__secondary_header['swath_number'], 2)}\n" +
            f"Number of Quads: {int(self.__secondary_header['num_quadratures'], 2)}\n"
        )