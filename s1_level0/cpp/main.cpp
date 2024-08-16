#include "packet_decoding.hpp"

using namespace std;


void print_packet_at_index(
    string filename,
    int index,
    bool headers = true,
    bool pulse_info = false,
    bool modes = false
) {
    std::ifstream data(filename, std::ios::binary);
    if (!data.is_open()) 
    {
        throw runtime_error("Unable to open: " + filename);
    }
    vector<L0Packet> packets = get_n_packets(data, index + 1, false, 0);

    if (index >= packets.size())
    {
        throw out_of_range("Index is greater than the number of packets.");
    }
    L0Packet packet = packets[index];

    if (headers)
    {
        packet.print_primary_header();
        packet.print_secondary_header();
    }
    if (pulse_info) packet.print_pulse_info();
    if (modes)      packet.print_modes();
}


int main(int argc, char* argv[]) 
{
    if(argv[1] == __null) 
    {
        cout << "Please enter a command." << endl;
        return 1;
    }

    string command = string(argv[1]);

    if (command == "print_nth_headers")
    {
        if(argv[2] == __null || argv[3] == __null) 
        {
            cout << "Please enter a packet index and filename." << endl;
            return 1;
        }
        string filename = string(argv[3]);
        print_packet_at_index(filename, stoi(argv[2]));
    }
    else if (command == "time_n")
    {
        if(argv[2] == __null || argv[3] == __null) 
        {
            cout << "Please enter the packet count to time and a filename." << endl;
            return 1;
        }

        string filename = string(argv[3]);
        ifstream data(filename, ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        int n = stoi(argv[2]);

        double runtime = time_packet_generation(data, n, false, 0);

        cout << "Decoded " << n << " packets in " << runtime << "s." << endl;
    }
    else if (command == "print_nth_pulse_info")
    {
        if(argv[2] == __null || argv[3] == __null) 
        {
            cout << "Please enter the packet index and filename." << endl;
            return 1;
        }
        int n = stoi(argv[2]);

        string filename = string(argv[3]);
        print_packet_at_index(filename, n, false, true);
    }
    else if (command == "print_nth_modes")
    {
        if(argv[2] == __null || argv[3] == __null) 
        {
            cout << "Please enter the packet index and filename." << endl;
            return 1;
        }
        int n = stoi(argv[2]);

        string filename = string(argv[3]);
        print_packet_at_index(filename, n, false, false, true);
    }
    else
    {
        cout << command << " is not a valid command." << endl;
    }

    // g++ -std=c++20 -O3 main.cpp -o main
    // Decoded single packet in 0.0277048s.
    // Decoded 100 packets in 1.34044s.
    // For Python, it was:
    // Decoded single packet in 0.5140669345855713s.
    // Decoded 100 packets in 50.56020474433899s.

    return 0;
}