#include <thread>

#include "packet_decoding.hpp"

using namespace std;


void complexer(vector<L0Packet>& packets, vector<vector<complex<double>>>& complex_samples)
{
    for (L0Packet packet : packets)
    {
        try
        {
            complex_samples.push_back(packet.get_complex_samples());
        }
        catch(...)
        {
            cout << "Error encountered." << endl;
            cout << "Sequence Count: " << packet.primary_header("packet_sequence_count") << endl;
            cout << "Data Length: " << packet.primary_header("packet_data_length") << endl;
            cout << "Data Format: " << packet.get_data_format() << endl;
            cout << "BAQ Mode: " << packet.get_baq_mode() << endl;
            cout << "Sensor Mode: " << packet.get_sensor_mode() << endl;
            cout << "Error Mode: " << packet.get_error_status() << endl;
            cout << "Quad Count: " << packet.get_num_quads() << endl;
            cout << "BAQ Block Count: " << packet.get_num_baq_blocks() << endl;
            cout << "" << endl;
        }
    }
}


void omp_test(ifstream& data)
{
    double runtime  = 0.0;

    vector<L0Packet> packets = get_all_packets(data, false, 10);

    int num_packets = packets.size();

    auto start = chrono::high_resolution_clock::now();

    #pragma omp parallel for
    for (int i = 0; i < num_packets; i++)
    {
        packets[i].get_complex_samples();
    }

    auto end = chrono::high_resolution_clock::now();

    chrono::duration<double> difference = end - start;

    cout << "Decoded " << num_packets << " packets in " << difference.count() << "s." << endl;
}


void thread_test(ifstream& data)
{
    double runtime  = 0.0;

    vector<L0Packet> packets = get_all_packets(data, false, 0);

    int num_packets = 50000;

    auto start = chrono::high_resolution_clock::now();


    vector<L0Packet> t1_packets = {packets.begin()        , packets.begin() + 12500};
    vector<L0Packet> t2_packets = {packets.begin() + 12500, packets.begin() + 25000};
    vector<L0Packet> t3_packets = {packets.begin() + 25000, packets.begin() + 37500};
    vector<L0Packet> t4_packets = {packets.begin() + 37500, packets.begin() + 50000};

    vector<vector<complex<double>>> t1_samples = {};
    vector<vector<complex<double>>> t2_samples = {};
    vector<vector<complex<double>>> t3_samples = {};
    vector<vector<complex<double>>> t4_samples = {};

    thread t1(ref(complexer), ref(t1_packets), ref(t1_samples));
    thread t2(ref(complexer), ref(t2_packets), ref(t2_samples));
    thread t3(ref(complexer), ref(t3_packets), ref(t3_samples));
    thread t4(ref(complexer), ref(t4_packets), ref(t4_samples));

    t1.join();
    t2.join();
    t3.join();
    t4.join();

    vector<vector<complex<double>>> complex_samples;

    for (vector<complex<double>> samples : t1_samples)
    {
        complex_samples.push_back(samples);
    }
    for (vector<complex<double>> samples : t2_samples)
    {
        complex_samples.push_back(samples);
    }
    for (vector<complex<double>> samples : t3_samples)
    {
        complex_samples.push_back(samples);
    }
    for (vector<complex<double>> samples : t4_samples)
    {
        complex_samples.push_back(samples);
    }

    auto end = chrono::high_resolution_clock::now();

    chrono::duration<double> difference = end - start;

    cout << "Decoded " << num_packets << " packets in " << difference.count() << "s." << endl;
}


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
    else if (command == "thread_test")
    {
        if(argv[2] == __null) 
        {
            cout << "Please enter the filename." << endl;
            return 1;
        }
        string filename = string(argv[2]);
        std::ifstream data(filename, std::ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        thread_test(data);
    }
    else if (command == "omp_test")
    {
        if(argv[2] == __null) 
        {
            cout << "Please enter the filename." << endl;
            return 1;
        }
        string filename = string(argv[2]);
        std::ifstream data(filename, std::ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        omp_test(data);
    }
    else if (command == "nth_complex_samples")
    {
        if(argv[2] == __null || argv[3] == __null) 
        {
            cout << "Please enter the packet index and filename." << endl;
            return 1;
        }
        int n = stoi(argv[2]);
        string filename = string(argv[3]);
        std::ifstream data(filename, std::ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        vector<L0Packet> packets = get_n_packets(data, n + 1, false, 0);
        vector<complex<double>> complex_samples = packets[n].get_complex_samples();
        for (complex<double> sample : complex_samples)
        {
            cout << "Complex Value: " << sample << endl;
        }
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