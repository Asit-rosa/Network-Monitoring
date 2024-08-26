import os
import time
import csv
from collections import defaultdict

# File path to the exported CSV file
file_path = 'packets_rtt.csv'

# Dictionary to hold request timestamps
requests = defaultdict(float)

def calculate_rtt_and_latency(file_path):
    global requests

    total_rtt = 0
    total_lat = 0
    count = 0

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            src_ip = row['ip.src']
            dst_ip = row['ip.dst']
            timestamp = float(row['frame.time_epoch'])
            seq_num = row['tcp.seq']
            ack_num = row['tcp.ack']
            packet_len = int(row['tcp.len'])

            if packet_len > 0:  # Assuming request packets have non-zero length
                if seq_num not in requests:
                    requests[seq_num] = timestamp
                elif ack_num:
                    request_time = requests.pop(seq_num, None)
                    if request_time:
                        rtt = timestamp - request_time
                        latency = rtt / 2
                        total_rtt += rtt
                        total_lat += latency
                        count += 1
                        print(f"Round-trip time: {rtt:.6f} seconds")
                        print(f"Estimated Latency: {latency:.6f} seconds")

    average_rtt = (total_rtt / count) if count > 0 else 0
    average_latency = (total_lat / count) if count > 0 else 0
    print(f"\nAverage Round-trip Time: {average_rtt:.6f} seconds")
    print(f"Average Latency: {average_latency:.6f} seconds")

# Clear the file initially
if os.path.exists(file_path):
    os.remove(file_path)

# Stop any previous tshark process capturing on wlp2s0
os.system("sudo pkill -f 'tshark -i wlp2s0'")

# Start tshark with IP filters and relevant fields
os.system(f"sudo tshark -i wlp2s0 -Y \"ip.src == 192.168.68.107 and ip.dst == 192.168.68.136\" -T fields -e frame.time_epoch -e ip.src -e ip.dst -e tcp.seq -e tcp.ack -e tcp.len -E header=y -E separator=, -E quote=d -E occurrence=f > {file_path} &")

# Real-time RTT and latency calculation every few seconds
while True:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        calculate_rtt_and_latency(file_path)
    time.sleep(1)
