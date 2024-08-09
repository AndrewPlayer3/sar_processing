import time

import numpy as np


def time_packet_generation(PacketGenerator, num_packets, perf_log_interval, log: bool = True):
    times = []
    for i in range(num_packets):
        start_time = time.time()
        _ = next(PacketGenerator)
        end_time = time.time()
        runtime = end_time - start_time
        times.append(runtime)
        if log and i % perf_log_interval == 0:
            print(f"Decoded Packet {i} of {num_packets} in {runtime}s.")
    time_arr = np.asarray(times)
    mean = time_arr.mean()
    total = sum(times)
    if log:
        print("---")
        print(f"Decoded {num_packets} in {total}s.")
        print("___")
        print(f"Mean Decoding Time: {mean}s.")
    return total, mean