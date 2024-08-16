#!/bin/bash

echo "Compiling main to bin/main."

g++ -std=c++20 -O3 main.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -o bin/main
