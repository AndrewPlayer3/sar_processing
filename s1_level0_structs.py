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
    24,  # SAS SSB Message *** TODO: See Page 43, 44
    24,  # SES SSB Message *** TODO: See Page 50
    16,  # Number of Quadratures
    8,   # N/A
]

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
    'sas_ssb_message',
    'ses_ssb_message',
    'num_quadratures',
    'na_5',
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
    ('tile_1_1', 0),
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
    'dummy_data': None,
    'x_axis_position': [0, 0, 0, 0],
    'y_axis_position': [0, 0, 0, 0],
    'z_axis_position': [0, 0, 0, 0],
    'x_axis_velocity': [0, 0],
    'y_axis_velocity': [0, 0],
    'z_axis_velocity': [0, 0],
    'pod_data_stamp': [0, 0, 0, 0],
    'q0_quaternion': [0, 0],
    'q1_quaternion': [0, 0],
    'q2_quaternion': [0, 0],
    'q3_quaternion': [0, 0],
    'omega_x': [0, 0],
    'omega_y': [0, 0],
    'omega_z': [0, 0],
    'data_time_stamp': [0, 0, 0, 0],
    'pointing_status': None,
    'temp_update_status': None,
    'tile_1_1': None,
    'tile_1_2': None,
    'tile_2_2': None,
    'tile_3_3': None,
    'tile_3_4': None,
    'tile_4_4': None,
    'tile_5_5': None,
    'tile_5_6': None,
    'tile_6_6': None,
    'tile_7_7': None,
    'tile_7_8': None,
    'tile_8_8': None,
    'tile_9_9': None,
    'tile_9_10': None,
    'tile_10_10': None,
    'tile_11_11': None,
    'tile_11_12': None,
    'tile_12_12': None,
    'tile_13_13': None,
    'tile_13_14': None,
    'tile_14_14': None,
    'na_tgu_temp': None
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