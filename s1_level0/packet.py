import numpy as np

from structs import (
    BRC_TO_HUFFMAN_START_BIT_LEN, 
    BRC_TO_HUFFMAN_CODING,
    BRC_TO_HUFFMAN_CODING_SET,
    SECONDARY_HEADER_SIZE,
    WORD_SIZE,
    SIMPLE_RECONSTRUCTION_METHOD,
    NORMALIZED_RECONSTRUCTION_LEVELS,
    THIDX_TO_SF_ARRAY,
    BRC_TO_THIDX,
    BRC_TO_M_CODE,
    ECC_CODE_TO_SENSOR_MODE,
    F_REF
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


    def num_quads(self) -> int:
        return self.__num_quads


    def num_baq_blocks(self) -> int:
        return self.__num_baq_blocks


    def test_mode(self) -> int:
        return self.__test_mode


    def baq_mode(self) -> int:
        return self.__baq_mode

    
    def user_data_length(self) -> int:
        return self.__user_data_length


    def data_format(self) -> str:
        return self.__data_format


    def get_tx_ramp_rate(self) -> np.float64:
        bits = self.__secondary_header['tx_ramp_rate']
        sign = -1 if bits[0] == '0' else 1
        tx_pulse_ramp_rate = sign * int(bits[1:16], 2) * (np.power(F_REF, 2) / 2097152)  # 2^21
        return tx_pulse_ramp_rate


    def get_start_frequency(self) -> np.float64:
        bits = self.__secondary_header['pulse_start_frequency']
        sign = -1 if bits[0] == '0' else 1
        txprr = self.get_tx_ramp_rate()
        tx_start_frequency = (txprr / (4 * F_REF)) + sign * int(bits[1:16], 2) * (F_REF / 16384)  # 2^14
        return tx_start_frequency
        

    def get_sensor_mode_str(self) -> str:
        ecc_code = int(self.__secondary_header['ecc_number'], 2)
        return ECC_CODE_TO_SENSOR_MODE[ecc_code]


    def get_polarization_str(self) -> str:
        pol_code = int(self.__secondary_header['polarisation'], 2)
        if 0 <= pol_code <= 3:
            return 'H'
        elif 4 <= pol_code <= 7:
            return 'V'
        else:
            raise ValueError(f'The Polarization Code is Invalid: {pol_code}')


    def get_test_mode_str(self) -> str:
        return {
            '000': 'measurement_mode',
            '001': 'n_a',
            '011': 'n_a',
            '100': 'contingency',
            '101': 'contingency',
            '110': 'test_mode_baq',
            '111': 'test_mode_bypass',
        }[self.__secondary_header['test_mode']]


    def get_rx_channel_id_str(self) -> str:
        rxchid_code = int(self.__secondary_header['rx_channel_id'], 2)
        if rxchid_code == 0:
            return 'V'
        elif rxchid_code == 1:
            return 'H'
        else:
            raise ValueError(f'The RX Channel ID is Invalid: {rxchid_code}')


    def get_baq_mode_str(self) -> str:
        baq_modes = {
            0: 'bypass_mode',
            3: '3_bit_mode',
            4: '4_bit_mode',
            5: '5_bit_mode',
            12: 'fdbaq_mode_0',
            13: 'fdbaq_mode_1',
            14: 'fdbaq_mode_2',
        }
        try:
            return baq_modes[self.__baq_mode]
        except KeyError:
            return 'n_a'


    def get_signal_type_str(self) -> str:
        signal_types = {
            0: 'echo',
            1: 'noise',
            8: 'tx_cal',
            9: 'rx_cal',
            10: 'epdn_cal',
            11: 'ta_cal',
            12: 'apdn_cal',
            15: 'txh_cal_iso'
        }
        signal_type = int(self.__secondary_header['signal_type'], 2)
        try:
            return signal_types[signal_type]
        except KeyError:
            return 'n_a'


    def get_sas_ssb(self):
        ssb_flag = self.__secondary_header['ssb_flag']
        if ssb_flag == '0':
            return {
                'ssb_flag': 0,
                'polarization': self.get_polarization_str(),
                'temperature_compensation': int(self.__secondary_header['temperature_compensation'], 2),
                'elevation_beam_address': int(self.__secondary_header['elevation_beam_address'], 2),
                'azimuth_beam_address': int(self.__secondary_header['azimuth_beam_address'], 2),
            }
        elif ssb_flag == '1':
            return {
                'ssb_flag': 1,
                'polarization': self.get_polarization_str(),
                'sas_test': 'test_mode' if self.__secondary_header['test_mode'] == '0' else 'normal',
                'calibration_type': int(self.__secondary_header['cal_type'], 2),
                'calibration_beam_address': int(self.__secondary_header['calibration_beam_address'], 2),
            }
        else:
            raise ValueError(f'SSB Flag is Invalid: {ssb_flag}')


    def get_primary_header(self) -> dict:
        primary_header = {
            'packet_version_number': int(self.__primary_header['packet_version_number'], 2),
            'packet_type': int(self.__primary_header['packet_type'], 2),
            'secondary_header_flag': int(self.__primary_header['secondary_header_flag'], 2),
            'process_id': int(self.__primary_header['process_id'], 2),
            'process_category': int(self.__primary_header['process_category'], 2),
            'packet_sequence_count': int(self.__primary_header['packet_sequence_count'], 2),
            'packet_data_length': int(self.__primary_header['packet_data_length'], 2),
        }
        return primary_header


    def get_secondary_header(self) -> dict:
        # TODO: The SAS SSB field is not handled in the decoding code.
        error_status = 'nominal' if int(self.__secondary_header['error_flag'], 2) == 0 else 'ssb corrupt'
        secondary_header = {
            'coarse_time': int(self.__secondary_header['coarse_time'], 2),
            'fine_time': int(self.__secondary_header['fine_time'], 2),
            'sync_marker': int(self.__secondary_header['sync_marker'], 2),
            'data_take_id': int(self.__secondary_header['data_take_id'], 2),
            'ecc': self.get_sensor_mode_str(),
            'test_mode': self.get_test_mode_str(),
            'rx_channel_id': self.get_rx_channel_id_str(),
            'instrument_configuration_id': int(self.__secondary_header['instrument_configuration_id'], 2),
            'sc_data_word_index': int(self.__secondary_header['sc_data_word_index'], 2),
            'sc_data_word': self.__secondary_header['sc_data_word'],
            'space_packet_count': int(self.__secondary_header['space_packet_count'], 2),
            'pri_count': int(self.__secondary_header['pri_count'], 2),
            'error_flag': error_status,
            'baq_mode': self.get_baq_mode_str(),
            'baq_block_length': 8 * (int(self.__secondary_header['baq_block_length'], 2) + 1),
            'range_decimation': int(self.__secondary_header['range_decimation'], 2),
            'rx_gain': -0.5 * int(self.__secondary_header['rx_gain'], 2),
            'tx_ramp_rate': self.get_tx_ramp_rate(),
            'tx_pulse_start_frequency': self.get_start_frequency(),
            'pulse_length': int(self.__secondary_header['pulse_length'], 2) / F_REF,
            'rank': int(self.__secondary_header['rank'], 2),
            'pri': int(self.__secondary_header['pri'], 2) / F_REF,
            'swst': int(self.__secondary_header['swst'], 2) / F_REF,
            'swl': int(self.__secondary_header['swl'], 2) / F_REF,
            'calibration_mode': int(self.__secondary_header['calibration_mode'], 2),
            'tx_pulse_number': int(self.__secondary_header['tx_pulse_number'], 2),
            'signal_type': self.get_signal_type_str(),
            'swap': int(self.__secondary_header['swap'], 2),
            'swath_number': int(self.__secondary_header['swath_number'], 2),
            'num_quads': self.__num_quads
        }
        for k, v in self.get_sas_ssb().items():
            secondary_header[k] = v
        return secondary_header


    def get_complex_samples(self):
        return self.__decode_user_data_field()


    def __jump_to_next_word_boundary(self, bit_string, num_bits) -> tuple[str, int]:
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
    ) -> tuple[list[int], list[int], str, int]:
        signs = []
        m_codes = []
        total_bits = 0
        num_s_codes = 128 if not last_block else self.__num_quads - (128 * (self.__num_baq_blocks - 1))
        for _ in range(num_s_codes):
            sign, bit_string = read_and_pop(bit_string, 1)
            m_code, bit_string, bit_len = huffman_decode(
                bit_string,
                BRC_TO_HUFFMAN_START_BIT_LEN[brc],
                BRC_TO_HUFFMAN_CODING_SET[brc],
                BRC_TO_HUFFMAN_CODING[brc]
            )
            signs.append(int(sign, 2))
            m_codes.append(m_code)
            total_bits += (bit_len + 1)
        return signs, m_codes, bit_string, total_bits


    def __type_d_decoder(self, bit_string, component: str) -> tuple[str, int]:
        brc_size = 3
        threshold_size = 8
        num_bits = 0
        total_bits = 0
        component_signs, component_m_codes = self.component_dict[component]
        for i in range(self.__num_baq_blocks):
            if component == 'IE':
                brc, bit_string = read_and_pop(bit_string, brc_size)
                brc = int(brc, 2)
                if brc > 4:
                    raise ValueError(f'Invalid BRC: {brc} at {i}')
                self.__brc.append(brc)
            if component == 'QE':
                threshold, bit_string = read_and_pop(bit_string, threshold_size)
                self.__thresholds.append([int(threshold, 2)])
            brc = self.__brc[i]
            last_block = i == self.__num_baq_blocks - 1
            signs, m_codes, bit_string, num_bits = self.__get_type_d_signs_and_m_codes(
                bit_string,
                self.__brc[i],
                last_block
            )
            component_signs.append(signs)
            component_m_codes.append(m_codes)
            brc_offset = brc_size if component == 'IE' else 0
            threshold_offset = threshold_size if component == 'QE' else 0
            total_bits += num_bits + brc_offset + threshold_offset
        bit_string, offset = self.__jump_to_next_word_boundary(bit_string, total_bits)
        return bit_string, total_bits + offset


    def __get_type_d_s_value(self, brc, threshold_index, m_code, sign) -> np.float64:
        thidx_comp_flag = BRC_TO_THIDX[brc]
        m_code_comp_flag = BRC_TO_M_CODE[brc]
        if threshold_index <= thidx_comp_flag:
            if m_code < m_code_comp_flag:
                return np.power(-1, sign) * m_code
            elif m_code == m_code_comp_flag:
                simple_recon = SIMPLE_RECONSTRUCTION_METHOD[1][brc][threshold_index]
                return np.power(-1, sign) * simple_recon
            else:
                raise ValueError(f'm_code not valid: {m_code}')
        elif threshold_index > thidx_comp_flag:
            normal_recon = NORMALIZED_RECONSTRUCTION_LEVELS[1][brc][m_code]
            sigma_factor = THIDX_TO_SF_ARRAY[threshold_index]
            return np.power(-1, sign) * normal_recon * sigma_factor


    def __type_d_s_value_reconstruction(self) -> None:
        s_values = []
        for block_id in range(self.__num_baq_blocks):
            brc = self.__brc[block_id]
            threshold_index = self.__thresholds[block_id][0]
            block_len = len(self.__ie_m_codes[block_id])
            for s_code_id in range(block_len):
                ie_sign, ie_m_code = self.__ie_signs[block_id][s_code_id], self.__ie_m_codes[block_id][s_code_id]
                io_sign, io_m_code = self.__io_signs[block_id][s_code_id], self.__io_m_codes[block_id][s_code_id]
                qe_sign, qe_m_code = self.__qe_signs[block_id][s_code_id], self.__qe_m_codes[block_id][s_code_id]
                qo_sign, qo_m_code = self.__qo_signs[block_id][s_code_id], self.__qo_m_codes[block_id][s_code_id]
                ie_s_value = self.__get_type_d_s_value(brc, threshold_index, ie_m_code, ie_sign)
                io_s_value = self.__get_type_d_s_value(brc, threshold_index, io_m_code, io_sign)
                qe_s_value = self.__get_type_d_s_value(brc, threshold_index, qe_m_code, qe_sign)
                qo_s_value = self.__get_type_d_s_value(brc, threshold_index, qo_m_code, qo_sign)
                component_s_values = [ie_s_value, io_s_value, qe_s_value, qo_s_value]
                s_values.append(component_s_values)
        complex_s_values = np.zeros((2 * self.__num_quads, ), dtype=complex)
        for i in range(1, self.__num_quads+1):
            ie, io, qe, qo = tuple(s_values[i-1])
            complex_s_values[2*i-2] = ie + 1j*qe
            complex_s_values[2*i-1] = io + 1j*qo
        return complex_s_values


    def __decode_type_d_data(self) -> None:
        self.__brc        = []
        self.__thresholds = []
        bit_counts = [0, 0, 0, 0]
        bit_string = create_bit_string(self.__raw_user_data)
        bit_string, bit_counts[0] = self.__type_d_decoder(bit_string, 'IE')
        bit_string, bit_counts[1] = self.__type_d_decoder(bit_string, 'IO')
        bit_string, bit_counts[2] = self.__type_d_decoder(bit_string, 'QE')
        bit_string, bit_counts[3] = self.__type_d_decoder(bit_string, 'QO')
        complex_s_values = self.__type_d_s_value_reconstruction()
        num_bytes = sum(bit_counts) / 8
        self.__raw_user_data = None
        self.__delete_codes()
        del self.__brc
        del self.__thresholds
        del self.__raw_user_data
        return complex_s_values, num_bytes


    def __type_a_b_s_value_reconstruction(self) -> None:
        s_values = []
        num_s_codes = len(self.__ie_signs)
        construct_s_value = lambda sign, m_code: np.power(-1, sign) * m_code
        for i in range(num_s_codes):
            ie_s_value = construct_s_value(self.__ie_signs[i], self.__ie_m_codes[i])
            io_s_value = construct_s_value(self.__io_signs[i], self.__io_m_codes[i])
            qe_s_value = construct_s_value(self.__qe_signs[i], self.__qe_m_codes[i])
            qo_s_value = construct_s_value(self.__qo_signs[i], self.__qo_m_codes[i])
            s_values.append([ie_s_value, io_s_value, qe_s_value, qo_s_value])
        complex_s_values = np.zeros((2 * len(self.s_values), ), dtype=complex)
        for i in range(1, self.__num_quads+1):
            ie, io, qe, qo = tuple(s_values[i-1])
            complex_s_values[2*i-2] = ie + 1j*qe
            complex_s_values[2*i-1] = io + 1j*qo
        return complex_s_values


    def __type_a_b_decoder(self, bit_string, component) -> tuple[str, int]:
        num_bits = 0
        sign_bits = 1
        m_code_bits = 9
        component_signs, component_m_codes = self.component_dict[component]
        for _ in range(self.__num_quads):
            sign, bit_string = read_and_pop(bit_string, sign_bits)
            m_code, bit_string = read_and_pop(bit_string, m_code_bits)
            component_signs.append(int(sign, 2))
            component_m_codes.append(int(m_code, 2))
            num_bits += 10
        bit_string, offset = self.__jump_to_next_word_boundary(bit_string, num_bits)
        return bit_string, num_bits + offset


    def __decode_type_a_b_data(self) -> None:
        bit_string = create_bit_string(self.__raw_user_data)
        bit_counts = [0, 0, 0, 0]
        bit_string, bit_counts[0] = self.__type_a_b_decoder(bit_string, 'IE')
        bit_string, bit_counts[1] = self.__type_a_b_decoder(bit_string, 'IO')
        bit_string, bit_counts[2] = self.__type_a_b_decoder(bit_string, 'QE')
        bit_string, bit_counts[3] = self.__type_a_b_decoder(bit_string, 'QO')
        complex_s_values = self.__type_a_b_s_value_reconstruction()
        num_bytes = sum(bit_counts) / 8
        self.__raw_user_data = None
        self.__delete_codes()
        del self.__raw_user_data
        return complex_s_values, num_bytes


    def __delete_codes(self):
        del self.__ie_signs
        del self.__ie_m_codes
        del self.__io_signs
        del self.__io_m_codes
        del self.__qe_signs
        del self.__qe_m_codes
        del self.__qo_signs
        del self.__qo_m_codes


    def __decode_user_data_field(self) -> None:
        self.__ie_signs, self.__ie_m_codes  = [], []
        self.__io_signs, self.__io_m_codes  = [], []
        self.__qe_signs, self.__qe_m_codes  = [], []
        self.__qo_signs, self.__qo_m_codes  = [], []
        self.component_dict = {
            'IE': (self.__ie_signs, self.__ie_m_codes),
            'IO': (self.__io_signs, self.__io_m_codes),
            'QE': (self.__qe_signs, self.__qe_m_codes),
            'QO': (self.__qo_signs, self.__qo_m_codes)
        }
        try:
            if self.__data_format == 'A':
                return self.__decode_type_a_b_data()
            elif self.__data_format == 'B':
                return self.__decode_type_a_b_data()
            elif self.__data_format == 'C':
                # Type C is not (forseen to be) used in nominal operation.
                # This will not be supported until I come across it.
                raise NotImplementedError("Data Format C is not supported.")
            elif self.__data_format == 'D':
                return self.__decode_type_d_data()
            else:
                raise ValueError('Packet does not have a valid data format.')
        except Exception as e:
            print(f"Error encountered with data format, skipping user data decoding: {e}")


    def __set_data_format(self) -> None:
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


    def __repr__(self) -> str:
        primary_header = self.get_primary_header()
        secondary_header = self.get_secondary_header()
        return (
            f"Packet Type: {self.__data_format}\n" +
            "--------------\n\n" +

            "Primary Header:\n" +
            "---------------\n" +
            f"Packet Version Number: {primary_header['packet_version_number']}\n" +
            f"Packet Type: {primary_header['packet_type']}\n" +
            f"Secondary Header Flag: {primary_header['secondary_header_flag']}\n" +
            f"Process ID: {primary_header['process_id']}\n" +
            f"Process Category: {primary_header['process_category']}\n" +
            f"Packet Sequence Count: {primary_header['packet_sequence_count']}\n" +
            f"Packet Data Length: {primary_header['packet_data_length']}\n\n" +

            f"Secondary Header:\n" +
            "-----------------\n" +
            f"Coarse Time: {secondary_header['coarse_time']}\n" +
            f"Fine Time: {secondary_header['fine_time']}\n" +
            f"Sync Marker: {secondary_header['sync_marker']}\n" +
            f"Data Take ID: {secondary_header['data_take_id']}\n" +
            f"Sensor Mode: {secondary_header['ecc']}\n" + 
            f"Test Mode: {secondary_header['test_mode']}\n" +
            f"RX Channel ID: {secondary_header['rx_channel_id']}\n" +
            f"Instrument Configuration ID: {secondary_header['instrument_configuration_id']}\n" +
            f"Sub-Commutative Word Index: {secondary_header['sc_data_word_index']}\n" +
            f"Sub-Commutative Word: {secondary_header['sc_data_word']}\n" +
            f"Space Packet Count: {secondary_header['space_packet_count']}\n" +
            f"PRI Count: {secondary_header['pri_count']}\n" +
            f"Error Flag: {secondary_header['error_flag']}\n" +
            f"BAQ Mode: {secondary_header['baq_mode']}\n" +
            f"BAQ Block Length: {secondary_header['baq_block_length']}\n" +
            f"Range Decimation: {secondary_header['range_decimation']}\n" +
            f"RX Gain: {secondary_header['rx_gain']}\n" +
            f"TX Ramp Rate: {secondary_header['tx_ramp_rate']}\n" +
            f"Pulse Start Frequency: {secondary_header['tx_pulse_start_frequency']}\n" +
            f"Pulse Length: {secondary_header['pulse_length']}\n" +
            f"Rank: {secondary_header['rank']}\n" +
            f"PRI: {secondary_header['pri']}\n" +
            f"SWST: {secondary_header['swst']}\n" +
            f"SWL: {secondary_header['swl']}\n" +
            f"SSB Flag: {secondary_header['ssb_flag']}\n" +
            f"Polarisation: {secondary_header['polarization']}\n" +
            f"Temperature Compensation: {secondary_header['temperature_compensation']}\n" +
            f"Elevation Beam Address: {secondary_header['elevation_beam_address']}\n" +
            f"Azimuth Beam Address: {secondary_header['azimuth_beam_address']}\n" +
            f"Calibration Mode: {secondary_header['calibration_mode']}\n" +
            f"TX Pulse Number: {secondary_header['tx_pulse_number']}\n" +
            f"Signal Type: {secondary_header['signal_type']}\n" +
            f"Swap: {secondary_header['swap']}\n" +
            f"Swath Number: {secondary_header['swath_number']}\n" +
            f"Number of Quads: {secondary_header['num_quads']}\n"
        )