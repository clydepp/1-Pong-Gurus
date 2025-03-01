import subprocess
import socket
import time 
import re
from collections import deque

window_size = 500
rtt_window = deque(maxlen=window_size)
total_rtt = 0

# Path to the Nios II Command Shell batch file
NIOS_CMD_SHELL_BAT = "C:/intelFPGA_lite/18.1/nios2eds/Nios_II_Command_Shell.bat"

print("We're in tcp client...");

#the server name and port client wishes to access
server_name = '18.171.239.69'

#'52.205.252.164'
server_port = 12000
#create a TCP client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Set up a TCP connection with the server
#connection_socket will be assigned to this client on the server side
client_socket.connect((server_name,server_port))

#return only the hex part. can be removed later for faster processing
def extract_hex(string):
    match = re.search(r'0x[0-9A-Fa-f]+', string)
    return match.group(0) if match else None  # Returns hex or None if not found


def stream_nios_console():
    """
    Continuously reads and outputs the contents of the Nios II console.
    """
    global total_rtt, rtt_window
    
    # Start the Nios II Command Shell and run nios2-terminal
    process = subprocess.Popen(
        [NIOS_CMD_SHELL_BAT, "nios2-terminal"],  # Run nios2-terminal directly
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.PIPE,  # Capture stderr
        text=True,  # Use text mode for easier string handling
    )

    print("Streaming Nios II console output... Press Ctrl+C to stop.")
    
    #time.sleep(3)
    
    try:
        while True:
            # Read a line from the console output
            output = process.stdout.readline().strip()
            
            if output:
                
                strip_output = output
                print(strip_output)  # Print the output to the console
                
                msg = strip_output
                    
                start_time = time.time()
                #send the message to the TCP server
                client_socket.send(msg.encode())

                #return values from the server 
                msg = client_socket.recv(1024)
                        
                end_time = time.time()
                rtt = (end_time-start_time)*1000 #convert to milliseconds
                        
                if len(rtt_window) == window_size:
                    total_rtt -= rtt_window[0] #remove oldest RTT
                         
                rtt_window.append(rtt)
                total_rtt += rtt
                moving_average = total_rtt/ len(rtt_window)
                        
                print(f"RTT: {rtt:.2f} ms | Moving Avg: {moving_average:.2f} ms")    
                print(msg.decode())    

            
                
            else:
                # If no output, check if the process has terminated
                if process.poll() is not None:
                    break
    except KeyboardInterrupt:
        print("Stopping console stream...")
    finally:
        # Terminate the process when done
        process.terminate()
        process.wait()
        print("Nios II console stream stopped.")

def main():
    """
    Main function to start streaming the Nios II console output.
    """
    stream_nios_console()
    
    client_socket.close()

if __name__ == "__main__":
    main()