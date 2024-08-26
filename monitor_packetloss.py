import csv
import time
import os

total_packets = 0
lost_packets = 0

def calculate_packet_loss(file_path):
    global total_packets, lost_packets

    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            total_packets += 1
            if row['tcp.analysis.retransmission'] or row['tcp.analysis.lost_segment'] or row['tcp.analysis.duplicate_ack'] or row['tcp.analysis.out_of_order']:
                lost_packets += 1

    packet_loss_percentage = (lost_packets / total_packets) * 100 if total_packets > 0 else 0
    return packet_loss_percentage

# File path to the exported CSV file
file_path = 'packets.csv'

# Clear the file initially
if os.path.exists(file_path):
    os.remove(file_path)

# Stop any previous tshark process capturing on wlp2s0
os.system("sudo pkill -f 'tshark -i wlp2s0'")

client_ip = "192.168.68.107"
server_ip = "192.168.68.136"
# Restart tshark with IP filters
os.system(f"sudo tshark -i wlp2s0 -Y \"ip.src == {client_ip} and ip.dst == {server_ip}\" -T fields -e frame.number -e ip.src -e ip.dst -e tcp.analysis.retransmission -e tcp.analysis.lost_segment -e tcp.analysis.duplicate_ack -e tcp.analysis.out_of_order -E header=y -E separator=, -E quote=d -E occurrence=f > {file_path} &")

# Real-time calculation every few seconds
while True:
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        packet_loss_percentage = calculate_packet_loss(file_path)
        print(f"Real-time Packet Loss Percentage: {packet_loss_percentage:.2f}%")
    time.sleep(1)
