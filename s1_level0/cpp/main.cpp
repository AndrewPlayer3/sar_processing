#include <chrono>

#include "packet.hpp"
#include "packet_decoding.hpp"

using namespace std;


int main(int argc, char* argv[]) 
{
    if(argv[1] == __null) 
    {
        cout << "Please enter a filename." << endl;
        return 1;
    }
    std::ifstream data(string(argv[1]), std::ios::binary);
    if (!data.is_open()) 
    {
        throw runtime_error("Unable to open: " + string(argv[1]));
    }

    L0Packet packet = get_next_packet(data);

    cout << "" << endl;
    packet.print_primary_header();
    cout << "" << endl;
    packet.print_secondary_header();
    cout << "" << endl;

    auto start = chrono::high_resolution_clock::now();
    vector<complex<double>> complex_samples = packet.get_complex_samples();
    auto end   = chrono::high_resolution_clock::now();

    chrono::duration<double> runtime = end - start;

    cout << "Decoded single packet in " << runtime.count() << "s." << endl;

    int num_packets = 60000;
    int log_interval = 1000;
    double total_runtime = 0.0;
    for (int i = 0; i < num_packets; i++)
    {
            auto start = chrono::high_resolution_clock::now();
            L0Packet packet = get_next_packet(data);          
            try
            {
                vector<complex<double>> complex_samples = packet.get_complex_samples();
            }
            catch(runtime_error)
            {
                continue;
            }

            auto end   = chrono::high_resolution_clock::now();

            chrono::duration<double> difference = end - start;
            total_runtime += difference.count();

            if (i % log_interval == 0 && i != 0)
            {
                cout << "Decoded " << i << " packets in " << total_runtime << "s." << endl;
            }
    }
    cout << "Decoded " << num_packets << " packets in " << total_runtime << "s." << endl;

    // g++ -std=c++20 -O3 main.cpp -o main
    // Decoded single packet in 0.0277048s.
    // Decoded 100 packets in 1.34044s.
    // For Python, it was:
    // Decoded single packet in 0.5140669345855713s.
    // Decoded 100 packets in 50.56020474433899s.

    return 0;
}