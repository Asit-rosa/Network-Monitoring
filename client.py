import socketio
import socket
import time
import requests
from pythonping import ping

sio = socketio.Client()

client_bytes_sent = 0
server_bytes_received = 0

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

def get_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None

@sio.on('server_bytes_received')
def on_server_bytes_received(data):
    global server_bytes_received
    server_bytes_received = data / 1024

def measure_latency(host):
    try:
        latency_ms = ping(host, count=5).rtt_avg_ms
        return latency_ms
    except Exception as e:
        print(f"Error measuring latency: {e}")
        return None

def check_server_response_time(host):
    try:
        target_url = f"http://{host}:5000"
        start_time = time.time()
        requests.get(target_url)
        end_time = time.time()
        response_time = end_time - start_time
        return response_time
    except requests.exceptions.RequestException as e:
        print(f"Error checking server response time: {e}")
        return None

def send_data_for_bandwidth(server_ip, server_port, data, num_bytes):
    global client_bytes_sent
    total_bytes_sent = 0
    start_time = time.time()

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, server_port))
            while total_bytes_sent < num_bytes:
                bytes_sent = s.send(data)
                total_bytes_sent += bytes_sent

        client_bytes_sent += (total_bytes_sent / 1024)

        end_time = time.time()
        elapsed_time = end_time - start_time
        bandwidth = (total_bytes_sent * 8) / elapsed_time  # bits per second
        bandwidth_kbps = bandwidth / 1000  # kilobits per second
        bandwidth_mbps = bandwidth_kbps / 1000  # megabits per second

        bandwidth_mbps = round(bandwidth_mbps, 2)

        return bandwidth_mbps
    except ConnectionResetError as e:
        return f"Connection reset by server: {e}"
    except Exception as e:
        return f"Error occurred: {e}"

def send_data_for_packetloss(server_ip, server_port, data, num_packets):
    total_packets_sent = 0
    lost_packets = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        for _ in range(num_packets):
            try:
                s.sendto(data, (server_ip, server_port))
                total_packets_sent += 1
            except socket.error:
                lost_packets += 1

    packet_loss_percentage = (lost_packets / num_packets) * 100
    return packet_loss_percentage

if __name__ == '__main__':
    try:
        sio.connect('http://192.168.68.114:5000')
    except socketio.exceptions.ConnectionError as e:
        print(f"SocketIO connection error: {e}")

    server_ip = '192.168.68.114'
    server_port_packetloss = 5001
    server_port_bandwidth = 5002
    data = b'X' * 1024  # 1 KB of data
    num_bytes = 10 * 1024 * 1024  # 10 MB of data
    num_packets = 100

    while True:
        latency = measure_latency('192.168.68.114')
        print(f"Latency: {latency} ms")
        sio.emit('latency', latency)

        response_time = check_server_response_time('192.168.68.114')
        response_time = round(response_time, 2)
        print(f"Response Time: {response_time} s")
        sio.emit('response_time', response_time)

        packetloss = send_data_for_packetloss(server_ip, server_port_packetloss, data, num_packets)
        print(f"Packet Loss: {packetloss} %")
        sio.emit('packet_loss', packetloss)

        bandwidth = send_data_for_bandwidth(server_ip, server_port_bandwidth, data, num_bytes)
        print(f"Bandwidth: {bandwidth} Mbps")
        sio.emit('bandwidth', bandwidth)

        client_bytes_sent = round(client_bytes_sent, 2)
        print(f"Client Bytes Sent: {client_bytes_sent} kb")
        sio.emit('client_bytes_sent', client_bytes_sent)

        server_bytes_received = round(server_bytes_received, 2)
        print(f"Server Bytes Received: {server_bytes_received} kb")

        print()

        time.sleep(1)

