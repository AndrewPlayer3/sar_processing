import numpy as np

from structs import (
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
    huffman_decode_for_brc,
)


class Packet:
    def __init__(
        self,
        primary_header,
        secondary_header,
        user_data_field
    ):
        self.primary_header   = primary_header
        self.secondary_header = secondary_header

        self.num_quads   = int(self.secondary_header['num_quadratures'], 2)
        self.num_samples = 2 * self.num_quads

        self.test_mode      = int(self.secondary_header['test_mode'], 2)
        self.baq_mode       = int(self.secondary_header['baq_mode'], 2)
        self.block_length   = int(self.secondary_header['baq_block_length'], 2)
        self.num_baq_blocks = int(np.ceil(2 * self.num_quads / 256))

        self.packet_data_length = int(primary_header['packet_data_length'], 2)
        self.user_data_length = (self.packet_data_length + 1) - SECONDARY_HEADER_SIZE
        self._raw_user_data = user_data_field
        self._set_data_format()
        self._decode_user_data_field()


    def _jump_to_next_word_boundary(self, bit_string, num_bits):
        offset = num_bits % WORD_SIZE
        if offset == 0:
            return bit_string, offset
        next_word_boundary = WORD_SIZE - offset
        _, bit_string = read_and_pop(bit_string, next_word_boundary)
        return bit_string, next_word_boundary


    def _set_num_words_type_d(self):
        num_words_ie = int(np.ceil(self.block_length * self.num_quads / WORD_SIZE))
        num_words_qe = int(np.ceil((self.block_length * self.num_quads + 8 * self.num_baq_blocks) / WORD_SIZE))
        self.num_words = (num_words_ie, num_words_qe)


    def _append_type_d_signs_and_m_codes(
        self,
        comp_signs: list,
        comp_m_codes: list,
        bit_string: str,
        brc: int,
        last_block: bool
    ) -> tuple[list[int], list[int], str]:
        signs = []
        m_codes = []
        s_code_count = 0
        total_bits = 0
        num_s_codes = 128 if not last_block else self.num_quads - (128 * (self.num_baq_blocks - 1))
        while s_code_count < num_s_codes:
            sign, bit_string = read_and_pop(bit_string, 1)
            m_code, bit_string, bit_len = huffman_decode_for_brc(bit_string, brc)
            signs.append(int(sign, 2))
            m_codes.append(m_code)
            s_code_count += 1
            total_bits += (bit_len + 1)
        comp_signs.append(signs)
        comp_m_codes.append(m_codes)
        return bit_string, total_bits


    def _type_d_decoder(self, bit_string, component: str):
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
        for i in range(self.num_baq_blocks):
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
            last_block = i == self.num_baq_blocks - 1
            bit_string, num_bits = self._append_type_d_signs_and_m_codes(
                comp_signs,
                comp_m_codes,
                bit_string,
                self.brc[i],
                last_block
            )
            brc_offset = brc_size if component == 'IE' else 0
            threshold_offset = threshold_size if component == 'QE' else 0
            total_bits += num_bits + brc_offset + threshold_offset
        bit_string, offset = self._jump_to_next_word_boundary(bit_string, total_bits)
        return bit_string, total_bits + offset


    def _get_type_d_s_value(self, brc, threshold_index, m_code, sign):
        thidx_comp_flag = BRC_TO_THIDX[brc]
        m_code_comp_flag = BRC_TO_M_CODE[brc]
        if threshold_index <= thidx_comp_flag:
            if m_code < m_code_comp_flag:
                return (-1 ** sign) * m_code
            elif m_code == m_code_comp_flag:
                simple_recon = SIMPLE_RECONSTRUCTION_METHOD[1][brc][threshold_index]
                return ((-1) ** sign) * simple_recon
        elif threshold_index > thidx_comp_flag:
            normal_recon = NORMALIZED_RECONSTRUCTION_LEVELS[1][brc][m_code]
            sigma_factor = THIDX_TO_SF_ARRAY[threshold_index]
            return (-1 ** sign) * normal_recon * sigma_factor


    def _type_d_s_value_reconstruction(self):
        self.s_values = []
        for block_id in range(self.num_baq_blocks):
            brc = self.brc[block_id]
            threshold_index = self.thresholds[block_id][0]
            block_len = len(self.ie_m_codes[block_id])
            for s_code_id in range(block_len):
                ie_s_value = self._get_type_d_s_value(brc, threshold_index, self.ie_m_codes[block_id][s_code_id], self.ie_signs[block_id][s_code_id])
                io_s_value = self._get_type_d_s_value(brc, threshold_index, self.io_m_codes[block_id][s_code_id], self.io_signs[block_id][s_code_id])
                qe_s_value = self._get_type_d_s_value(brc, threshold_index, self.qe_m_codes[block_id][s_code_id], self.qe_signs[block_id][s_code_id])
                qo_s_value = self._get_type_d_s_value(brc, threshold_index, self.qo_m_codes[block_id][s_code_id], self.qo_signs[block_id][s_code_id])
                component_s_values = [ie_s_value, io_s_value, qe_s_value, qo_s_value]
                self.s_values.append(component_s_values)
        complex_s_value = np.zeros((2 * self.num_quads, ), dtype=complex)
        for i in range(1, self.num_quads+1):
            ie, io, qe, qo = tuple(self.s_values[i-1])
            complex_s_value[2*i-2] = ie + 1j*qe
            complex_s_value[2*i-1] = io + 1j*qo
        self.complex_s_values = complex_s_value


    def _decode_type_d_data(self):    
        self._set_num_words_type_d()
        self.brc        = []
        self.thresholds = []
        self.ie_signs, self.ie_m_codes  = [], []
        self.io_signs, self.io_m_codes  = [], []
        self.qe_signs, self.qe_m_codes  = [], []
        self.qo_signs, self.qo_m_codes  = [], []
        bit_string = create_bit_string(self._raw_user_data)
        bit_string, self.num_ie_bits = self._type_d_decoder(bit_string, 'IE')
        bit_string, self.num_io_bits = self._type_d_decoder(bit_string, 'IO')
        bit_string, self.num_qe_bits = self._type_d_decoder(bit_string, 'QE')
        bit_string, self.num_qo_bits = self._type_d_decoder(bit_string, 'QO')
        self.remaining_user_data_bits = len(bit_string)
        self._type_d_s_value_reconstruction()
        self._raw_user_data = None
        del self._raw_user_data


    def _decode_user_data_field(self):
        if self.data_format == 'A':
            pass
        elif self.data_format == 'B':
            pass
        elif self.data_format == 'C':
            pass
        elif self.data_format == 'D':
            self._decode_type_d_data()


    def _set_data_format(self):
        self.test_mode = int(self.secondary_header['test_mode'], 2)
        self.baq_mode  = int(self.secondary_header['baq_mode'], 2)
        if self.baq_mode == 0:
            if self.test_mode % 3 == 0:
                self.data_format = 'A'
            else:
                self.data_format = 'B'
        elif self.baq_mode in [3, 4, 5]:
            self.data_format = 'C'
        elif self.baq_mode in [12, 13, 14]:
            self.data_format = 'D'
        else:
            raise ValueError(f'No Data Format with BAQ Mode: {self.baq_mode} and Test Mode: {self.test_mode}')
