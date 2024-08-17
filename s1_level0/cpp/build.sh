#!/bin/bash

echo "Compiling main to bin/main."

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
	g++ -fopenmp -std=c++20 -O3 main.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -o bin/main
elif [[ "$OSTYPE" == "darwin"* ]]; then
	/opt/homebrew/opt/llvm/bin/clang++ -fopenmp -std=c++20 -O3 main.cpp packet.cpp packet_decoding.cpp decoding_utils.cpp -o bin/main
else
	echo "$OSTYPE is not supported by this script, see the commands for what needs to be compiled."
fi
