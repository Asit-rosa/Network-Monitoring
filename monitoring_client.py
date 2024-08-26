import multiprocessing
import socketio
import time
import os

# Initialize a Socket.IO client
sio = socketio.Client()
sio.connect('http://192.168.68.136:8585')

@sio.event
def connect():
    print('Connected to the server')

@sio.event
def disconnect():
    print('Disconnected from the server')

def Latency():
    @sio.on('Latency')
    def latency(data):
        print(f"Latency: {data:.2f} ms")

def Response_Time():
    @sio.on('Response Time')
    def response_time(data):
        print(f"Server Response Time: {data:.2f} s")

def packetloss():
    os.system("python3 monitor_packetloss.py")

def bandwidth():
    os.system("python3 monitor_bandwidth.py")

if __name__ == "__main__":
    # Clear the console to start with clean output
    os.system('clear')

    # Create separate processes for packetloss and bandwidth monitoring
    latency_process = multiprocessing.Process(target=Latency())
    response_time_process = multiprocessing.Process(target=Response_Time())
    packetloss_process = multiprocessing.Process(target=packetloss)
    bandwidth_process = multiprocessing.Process(target=bandwidth)

    # Start both processes
    latency_process.start()
    response_time_process.start()
    packetloss_process.start()
    bandwidth_process.start()

    # Continuously monitor and print their outputs separately
    while True:
        time.sleep(1)  # Adjust the sleep duration as needed

        if not latency_process.is_alive() or not response_time_process.is_alive() or not packetloss_process.is_alive() or not bandwidth_process.is_alive():
            print("One of the processes has terminated.")
            break

    # Ensure both processes are terminated properly
    latency_process.join()
    response_time_process.join()
    packetloss_process.join()
    bandwidth_process.join()