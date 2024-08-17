#include <thread>

#include "packet_decoding.hpp"

using namespace std;


void omp_test(ifstream& data)
{
    vector<L0Packet> packets = get_all_packets(data, false, 10);

    const int num_packets = packets.size();

    chrono::time_point start = chrono::high_resolution_clock::now();

    vector<vector<complex<double>>> complex_samples(num_packets);

    #pragma omp parallel for
    for (int i = 0; i < num_packets; i++)
    {
        complex_samples[i] = packets[i].get_complex_samples();
    }

    chrono::time_point end = chrono::high_resolution_clock::now();

    chrono::duration<double> difference = end - start;

    cout << "Decoded " << num_packets << " packets in " << difference.count() << "s." << endl;
}


void thread_runner(
    vector<vector<complex<double>>>& complex_samples,
    vector<L0Packet>& packets,
    const int start_index,
    const int end_index
)
{
    for (int i = start_index; i < end_index; i++)
    {
        complex_samples[i] = packets[i].get_complex_samples();
    }
}


void thread_test(ifstream& data)
{
    vector<L0Packet> packets = get_all_packets(data, false, 0);
    vector<thread>   threads;

    const int num_packets = packets.size();
    const int num_threads = thread::hardware_concurrency();
    const int chunk_size  = num_packets / num_threads;

    chrono::time_point start = chrono::high_resolution_clock::now();

    vector<vector<complex<double>>> complex_samples(num_packets);

    for (int i = 0; i < num_threads; i++)
    {
        int start_index =  i * chunk_size;
        int end_index   = (i == num_threads - 1) ? num_packets : start_index + chunk_size;
        
        threads.emplace_back(
            thread_runner,
            ref(complex_samples),
            ref(packets),
            start_index,
            end_index
        );
    }

    for (thread& thread : threads)
    {
        if (thread.joinable()) thread.join();
    }

    chrono::time_point end = chrono::high_resolution_clock::now();

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
    else if (command == "check_packet_types")
    {
        string filename = string(argv[2]);
        std::ifstream data(filename, std::ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        vector<L0Packet> packets = get_all_packets(data, false, 0);
        for (int i = 0; i < packets.size(); i++)
        {
            L0Packet packet = packets[i];
            char data_format    = packet.get_data_format();
            int  sequence_count = packet.primary_header("packet_sequence_count");
            if (data_format != 'D')
            {
                cout << "Packet #" << sequence_count << " at index " << i << " is type " << data_format << endl;
            }
        }
    }
    else if (command == "nth_packet_type")
    {
        string filename = string(argv[3]);
        std::ifstream data(filename, std::ios::binary);
        if (!data.is_open()) 
        {
            throw runtime_error("Unable to open: " + filename);
        }
        int n = stoi(argv[2]);
        vector<L0Packet> packets = get_n_packets(data, n + 1, false, 0);
        cout << "Packet Type is " << packets[n].get_data_format() << "." << endl;
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