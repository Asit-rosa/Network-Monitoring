import subprocess

def run_iftop(interface, src_ip, dst_ip):
    command = [
        "sudo", "iftop", "-i", "wlp2s0",
        "-f", f"tcp and (src host 192.168.68.107 and dst host 192.168.68.136)",
        "-t", "-n", "-P", "-B" 
    ]

    # Run the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    interface = "wlp2s0"
    src_ip = "192.168.68.107"
    dst_ip = "192.168.68.136"
    run_iftop(interface, src_ip, dst_ip)
