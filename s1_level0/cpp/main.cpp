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

    L0Packet packet = decode_next_packet(data);

    cout << "" << endl;
    packet.print_primary_header();
    cout << "" << endl;
    packet.print_secondary_header();

    std::ifstream index_data(string(argv[2]), std::ios::binary);
    if (!index_data.is_open()) 
    {
        throw runtime_error("Unable to open: " + string(argv[2]));
    }

    vector<unordered_map<string, int>> index_records = index_decoder(index_data);

    index_data.close();

    std::ifstream annot_data(string(argv[3]), std::ios::binary);
    if (!annot_data.is_open()) 
    {
        throw runtime_error("Unable to open: " + string(argv[3]));
    }

    vector<unordered_map<string, int>> annotation_records = annotation_decoder(annot_data);

    annot_data.close();

    cout << "" << endl;
    cout << "Number of Index Records: " << index_records.size() << endl;
    cout << "Number of Annotation Records: " << annotation_records.size() << endl;
    cout << "" << endl;    

    auto start = chrono::high_resolution_clock::now();
    vector<complex<double>> complex_samples = packet.get_complex_samples();
    auto end   = chrono::high_resolution_clock::now();

    chrono::duration<double> runtime = end - start;

    cout << "Decoded single packet in " << runtime.count() << "s.\n" << endl;

    double total_runtime = time_packet_generation(data, 60000, true, 1000); 

    // g++ -std=c++20 -O3 main.cpp -o main
    // Decoded single packet in 0.0277048s.
    // Decoded 100 packets in 1.34044s.
    // For Python, it was:
    // Decoded single packet in 0.5140669345855713s.
    // Decoded 100 packets in 50.56020474433899s.

    return 0;
}