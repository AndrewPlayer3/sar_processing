PRIMARY_HEADER = [
    3,   # Packet Version Number
    1,   # Packet Type
    1,   # Secondary Header Flag
    7,   # Process ID
    4,   # Process Category
    2,   # Sequence Flags
    14,  # Packet Sequence Count 
    16   # Packet Data Length
]

PRIMARY_HEADER_FIELDS = [
    'packet_version_number',
    'packet_type',
    'secondary_header_flag',
    'process_id',
    'process_category',
    'sequence_flags',
    'packet_sequence_count',
    'packet_data_length'
]


SECONDARY_HEADER = [
    32,  # Coarse Time
    16,  # Fine Time
    32,  # Sync Marker
    32,  # Data Take ID
    8,   # ECC Number
    1,   # N/A
    3,   # Test Mode
    4,   # RX Channel ID
    32,  # Instrument Configuration ID
    8,   # Sub-Commutative Ancillary Data Word Index
    16,  # Sub-Commutative Ancillary Data Word
    32,  # Counter Service
    32,  # PRI Count
    1,   # Error Flag
    2,   # N/A
    5,   # BAQ Mode
    8,   # BAQ Block Length
    8,   # N/A
    8,   # Range Decimation
    8,   # RX Gain
    16,  # TX Ramp Rate
    16,  # Pulse Start Frequency
    24,  # Pulse Length
    3,   # N/A
    5,   # Rank
    24,  # PRI
    24,  # SWST
    24,  # SWL
    1,   # SSB Flag - "Imaging Mode" is 0, "Calibration Mode" is 1
    3,   # Polarisation
    2,   # Temperature Compensation
    2,   # N/A
    4,   # Elevation Beam Address or "SAS Test"
    2,   # N/A
    10,  # Azimuth Beam Address or Calibration Beam Address
    2,   # Calibration Mode
    1,   # N/A
    5,   # TX Pulse Number
    4,   # Signal Type
    3,   # N/A
    1,   # Swap
    8,   # Swath Number
    16,  # Number of Quadratures
    8,   # N/A
]


# SAS_SSB_MESSAGE = [
#     1,  # SSB Flag - "Imaging Mode" is 0, "Calibration Mode" is 1
#     3,  # Polarisation
#     2,  # Temperature Compensation
#     2,  # N/A
#     4,  # Elevation Beam Address or "SAS Test"
#     2,  # N/A
#     10, # Azimuth Beam Address or Calibration Beam Address
# ]


# SES_SSB_MESSAGE = [
#     2,  # Calibration Mode
#     1,  # N/A
#     5,  # TX Pulse Number
#     4,  # Signal Type
#     3,  # N/A
#     1,  # Swap
#     8,  # Swath Number
# ]


# {'coarse_time': '01010011110111001110110100101010',
#  'fine_time': '0001111001001101',
#  'sync_marker': '00110101001011101111100001010011',
#  'data_take_id': '00001101011011010001010111000000',
#  'ecc_number': '00001000',
#  'na_1': '0',
#  'test_mode': '000',
#  'rx_channel_id': '0000',
#  'instrument_configuration_id': '00000000000000000000000000000111',
#  'sc_data_word_index': '00011011',
#  'sc_data_word': '1011111011000011',
#  'counter_service': '00000000000000111010101110010101',
#  'pri_count': '00000000000000111011011010111000',
#  'error_flag': '0',
#  'na_2': '00',
#  'baq_mode': '01100',
#  'baq_block_length': '00011111',
#  'na_3': '00000000',
#  'range_decimation': '00001000',
#  'rx_gain': '00001000',
#  'tx_ramp_rate': '1000011001000101',
#  'pulse_start_frequency': '0011000000101111',
#  'pulse_length': '000000000000011110101111',
#  'na_4': '000',
#  'rank': '01001',
#  'pri': '000000000101010101100011',
#  'swst': '000000000000111001100001',
#  'swl': '000000000011011010011011',
#  'ssb_flag': '0',
#  'polarisation': '111',
#  'temperature_compensation': '11',
#  'na_5': '00',
#  'elevation_beam_address': '0110',
#  'na_6': '00',
#  'azimuth_beam_address': '0110000001',
#  'calibration_mode': '00',
#  'na_7': '0',
#  'tx_pulse_number': '00110',
#  'signal_type': '0000',
#  'na_8': '000',
#  'swap': '1',
#  'swath_number': '00001010',
#  'num_quadratures': '0010111010100010',
#  'na_9': '00000000'}



SECONDARY_HEADER_FIELDS = [
    'coarse_time',
    'fine_time',
    'sync_marker',
    'data_take_id',
    'ecc_number',
    'na_1',
    'test_mode',
    'rx_channel_id',
    'instrument_configuration_id',
    'sc_data_word_index',
    'sc_data_word',
    'counter_service',
    'pri_count',
    'error_flag',
    'na_2',
    'baq_mode',
    'baq_block_length',
    'na_3',
    'range_decimation',
    'rx_gain',
    'tx_ramp_rate',
    'pulse_start_frequency',
    'pulse_length',
    'na_4',
    'rank',
    'pri',
    'swst',
    'swl',
    'ssb_flag',
    'polarisation',
    'temperature_compensation',
    'na_5',
    'elevation_beam_address',
    'na_6',
    'azimuth_beam_address',
    'calibration_mode',
    'na_7',
    'tx_pulse_number',
    'signal_type',
    'na_8',
    'swap',
    'swath_number',
    'num_quadratures',
    'na_9',
]


SUB_COMM_KEY_POS = [
    ('dummy_data', 0),
    ('x_axis_position', 0),
    ('x_axis_position', 1),
    ('x_axis_position', 2),
    ('x_axis_position', 3),
    ('y_axis_position', 0),
    ('y_axis_position', 1),
    ('y_axis_position', 2),
    ('y_axis_position', 3),
    ('z_axis_position', 0),
    ('z_axis_position', 1),
    ('z_axis_position', 2),
    ('z_axis_position', 3),
    ('x_axis_velocity', 0),
    ('x_axis_velocity', 1),
    ('y_axis_velocity', 0),
    ('y_axis_velocity', 1),
    ('z_axis_velocity', 0),
    ('z_axis_velocity', 1),
    ('pod_data_stamp', 0),
    ('pod_data_stamp', 1),
    ('pod_data_stamp', 2),
    ('pod_data_stamp', 3),
    ('q0_quaternion', 0),
    ('q0_quaternion', 1),
    ('q1_quaternion', 0),
    ('q1_quaternion', 1),
    ('q2_quaternion', 0),
    ('q2_quaternion', 1),
    ('q3_quaternion', 0),
    ('q3_quaternion', 1),
    ('omega_x', 0),
    ('omega_x', 1),
    ('omega_y', 0),
    ('omega_y', 1),
    ('omega_z', 0),
    ('omega_z', 1),
    ('data_time_stamp', 0),
    ('data_time_stamp', 1),
    ('data_time_stamp', 2),
    ('data_time_stamp', 3),
    ('pointing_status', 0),
    ('temp_update_status', 0),
    ('tile_1_1', 0, ),
    ('tile_1_2', 0),
    ('tile_2_2', 0),
    ('tile_3_3', 0),
    ('tile_3_4', 0),
    ('tile_4_4', 0),
    ('tile_5_5', 0),
    ('tile_5_6', 0),
    ('tile_6_6', 0),
    ('tile_7_7', 0),
    ('tile_7_8', 0),
    ('tile_8_8', 0),
    ('tile_9_9', 0),
    ('tile_9_10', 0),
    ('tile_10_10', 0),
    ('tile_11_11', 0),
    ('tile_11_12', 0),
    ('tile_12_12', 0),
    ('tile_13_13', 0),
    ('tile_13_14', 0),
    ('tile_14_14', 0),
    ('na_tgu_temp', 0),
]


SUB_COMM_KEY_VAL = {
    'dummy_data': '0000000000000000',
    'x_axis_position':'0000000000000000000000000000000000000000000000000000000000000000',
    'y_axis_position': '0000000000000000000000000000000000000000000000000000000000000000',
    'z_axis_position': '0000000000000000000000000000000000000000000000000000000000000000',
    'x_axis_velocity': '00000000000000000000000000000000',
    'y_axis_velocity': '00000000000000000000000000000000',
    'z_axis_velocity': '00000000000000000000000000000000',
    'pod_data_stamp': '00000000000000000000000000000000',
    'q0_quaternion': '00000000000000000000000000000000',
    'q1_quaternion': '00000000000000000000000000000000',
    'q2_quaternion': '00000000000000000000000000000000',
    'q3_quaternion': '00000000000000000000000000000000',
    'omega_x': '00000000000000000000000000000000',
    'omega_y': '00000000000000000000000000000000',
    'omega_z': '00000000000000000000000000000000',
    'data_time_stamp': '0000000000000000000000000000000000000000000000000000000000000000',
    'pointing_status': '0000000000000000',
    'temp_update_status': '0000000000000000',
    'tile_1_1': '0000000000000000',
    'tile_1_2': '0000000000000000',
    'tile_2_2': '0000000000000000',
    'tile_3_3': '0000000000000000',
    'tile_3_4': '0000000000000000',
    'tile_4_4': '0000000000000000',
    'tile_5_5': '0000000000000000',
    'tile_5_6': '0000000000000000',
    'tile_6_6': '0000000000000000',
    'tile_7_7': '0000000000000000',
    'tile_7_8': '0000000000000000',
    'tile_8_8': '0000000000000000',
    'tile_9_9': '0000000000000000',
    'tile_9_10': '0000000000000000',
    'tile_10_10': '0000000000000000',
    'tile_11_11': '0000000000000000',
    'tile_11_12': '0000000000000000',
    'tile_12_12': '0000000000000000',
    'tile_13_13': '0000000000000000',
    'tile_13_14': '0000000000000000',
    'tile_14_14': '0000000000000000',
    'na_tgu_temp': '0000000000000000'
}


SUB_COMMUTATIVE_DATA_SERVICE = [
    16,      # Dummy Data
    64,      # X-Axis ECEF Position
    64,      # Y-Axis ECEF Position
    64,      # Z-Axis ECEF Position
    32,      # X-velocity ECEF
    32,      # Y-velocity ECEF
    32,      # Z-velocity ECEF
    16,      # POD Data Stamp 1
    16,      # Pod Data Stamp 2
    16,      # Pod Data Stamp 3
    16,      # Pod Data Stamp 4
    32,      # Q0 Attitude Quaternion
    32,      # Q1 Attitude Quaternion
    32,      # Q2 Attitude Quaternion
    32,      # Q3 Attitude Quaternion
    32,      # OmegaX Angular Rate
    32,      # OmegaY Angular Rate
    32,      # OmegaZ Angular Rate
    16,      # Data Time Stamp 1
    16,      # Data Time Stamp 2
    16,      # Data Time Stamp 3
    16,      # Data Time Stamp 4
    16,      # Pointing Status
    16,      # Temperature Update Status
    8, 8, 8, # Tile 1 EFE H, V Temperature and Activate TA Temperature
    8, 8, 8, # Tile 2
    8, 8, 8, # Tile 3
    8, 8, 8, # Tile 4
    8, 8, 8, # Tile 5
    8, 8, 8, # Tile 6
    8, 8, 8, # Tile 7
    8, 8, 8, # Tile 8
    8, 8, 8, # Tile 9
    8, 8, 8, # Tile 10
    8, 8, 8, # Tile 11
    8, 8, 8, # Tile 12
    8, 8, 8, # Tile 13
    8, 8, 8, # Tile 14
    9,       # N/A
    7,       # TGU Temperature
]