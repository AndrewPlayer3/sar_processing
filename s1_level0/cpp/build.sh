#!/bin/bash

echo "Compiling main to bin/main."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	g++ -fopenmp -std=c++20 -O3 main.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -o bin/main
elif [[ "$OSTYPE" == "darwin"* ]]; then
	/opt/homebrew/opt/llvm/bin/clang++ -fopenmp -std=c++20 -O3 main.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -o bin/main
else
	echo "$OSTYPE is not supported by this script, see the commands for what needs to be compiled."
fi
 
echo "Compiling plotting to bin/plot"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	g++ -fopenmp -std=c++20 -O3 -w plotting.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -I/usr/include/python3.12 -I$HOME/miniforge3/envs/signal_processing/lib/python3.12/site-packages/numpy/_core/include -lpython3.12 -o bin/plot
elif [[ "$OSTYPE" == "darwin"* ]]; then
	/opt/homebrew/opt/llvm/bin/clang++ -fopenmp -std=c++20 -O3 -w plotting.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -I/usr/include/python3.12 -I$HOME/miniforge3/envs/signal_processing/lib/python3.12/site-packages/numpy/_core/include -lpython3.12 -o bin/plot
else
	echo "$OSTYPE is not supported by this script, see the commands for what needs to be compiled."
fi