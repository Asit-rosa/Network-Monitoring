import socket
import socketio
import eventlet
import threading

sio = socketio.Server(cors_allowed_origins='*')
app = socketio.WSGIApp(sio)

# Variables to track network traffic
server_bytes_received = 0

def get_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print("Error:", e)
        return None

@sio.event
def connect(sid, environ):
    print('Client connected', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected', sid)

@sio.on('latency')
def get_latency(sid, data):
    print('latency', data)
    sio.emit('latency', data)

@sio.on('response_time')
def get_response_time(sid, data):
    print('response_time', data)
    sio.emit('response_time', data)

@sio.on('packet_loss')
def get_packet_loss(sid, data):
    print('packet_loss', data)
    sio.emit('packet_loss', data)

@sio.on('bandwidth')
def get_bandwidth(sid, data):
    print('bandwidth', data)
    sio.emit('bandwidth', data)

@sio.on('client_bytes_sent')
def get_client_bytes_sent(sid, data):
    global server_bytes_received
    print(f"client_bytes_sent {data}")
    sio.emit('client_bytes_sent', data)
    print(f"server_bytes_received {server_bytes_received}")
    sio.emit('server_bytes_received', server_bytes_received)

def receive_data_for_bandwidth(bind_ip, bind_port):
    global server_bytes_received
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((bind_ip, bind_port))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print(f'Connected by {addr}')
                try:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        server_bytes_received += len(data)
                except ConnectionResetError as e:
                    print(f"Connection was reset by the client: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")

def receive_data_for_packetloss(bind_ip, bind_port, expected_packets):
    received_packets = 0
    lost_packets = 0

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((bind_ip, bind_port))
        while received_packets < expected_packets:
            data, _ = s.recvfrom(1024)
            if data:
                received_packets += 1
            else:
                lost_packets += 1

    packet_loss_percentage = (lost_packets / expected_packets) * 100
    print(f"Packet Loss Percentage: {packet_loss_percentage}%")
    return packet_loss_percentage

@sio.on('client_bytes_sent')
def get_client_bytes_sent(sid, data):
    global server_bytes_received
    print(f"client_bytes_sent {data}")
    sio.emit('client_bytes_sent', data)
    print(f"server_bytes_received {server_bytes_received}")
    sio.emit('server_bytes_received', server_bytes_received)

if __name__ == '__main__':
    bind_ip = '192.168.68.114'
    bind_port_packetloss = 5001  # Ensure this port matches the client configuration
    bind_port_bandwidth = 5002
    expected_packets = 100  # Number of packets expected to receive

    # Start the socketio server
    wsgi_thread = threading.Thread(target=eventlet.wsgi.server, args=(eventlet.listen((get_ip(), 5000)), app))
    wsgi_thread.start()

    # Start the TCP server for receiving data
    tcp_server_thread = threading.Thread(target=receive_data_for_bandwidth, args=(bind_ip, bind_port_bandwidth))
    tcp_server_thread.start()

    # Start the UDP server for packet loss
    udp_server_thread = threading.Thread(target=receive_data_for_packetloss, args=(bind_ip, bind_port_packetloss, expected_packets))
    udp_server_thread.start()
