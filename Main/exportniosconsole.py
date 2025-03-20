import asyncio
from collections import deque
import json

# Server details
SERVER_HOST = "13.40.56.220"
SERVER_PORT = 12000
NIOS_CMD_SHELL_BAT = "C:/intelFPGA_lite/18.1/nios2eds/Nios_II_Command_Shell.bat"

# RTT Tracking
# window_size = 500
# rtt_window = deque(maxlen=window_size)
# total_rtt = 0

# Shared Variables
strip_output = None
decoded_msg = None
writer = None
strip_output_event = asyncio.Event()  # Async event for signaling new messages
username_available_event = asyncio.Event()  # Async event for signaling username availability
ballpos_available_event = asyncio.Event()
winner_available_event = asyncio.Event()
username = None # Username for the client
win = False
side = None # side of player
ballposx = None
ballposy= None
ballside = None


async def stream_nios_console():
    
    global strip_output
    # Start async subprocess for nios2-terminal
    process = await asyncio.create_subprocess_exec(
        NIOS_CMD_SHELL_BAT, "nios2-terminal",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    try:
        while True:
            # Read a line asynchronously
            output = await process.stdout.readline()
            output = output.decode().strip()

            if output:
                strip_output = output
                strip_output_event.set()  # Signal that new data is available
    except asyncio.CancelledError:
        print("Stopping Nios II console stream...")
    finally:
        process.terminate()
        await process.wait()
        print("Nios II console stream stopped.")

async def send_messages(writer):
    # asnychronously send messages to the server
    global strip_output
    
    try:
        while True:
            await strip_output_event.wait()  # Wait for new console output
            strip_output_event.clear()
            
            if strip_output:
                message = strip_output
                print(f"Message: {message}")
                
                writer.write(message.encode())
                await writer.drain()
                
            await asyncio.sleep(0.05)  # Allow time for next message
    except asyncio.CancelledError:
        print("Sending messages task cancelled.")
        
async def send_json(data, writer):
    global strip_output
    
    if writer is None:
        print("Error: No active connection to the server.")
        return
    
    try:
        # Serialise data as JSON and send
        json_data = json.dumps(data)
        strip_output = json_data
        strip_output_event.set()
        await writer.drain()
        print(f"Sent: {json_data}")
    except Exception as e:
        print(f"Error sending json: {e}")
        
async def send_username(writer):
    global username, side
    try:
        while True:
            await username_available_event.wait()
            username_available_event.clear()
            
            if username:
                data = {
                    "username": username,
                    "side": side
                }
                
                await send_json(data, writer)
    except asyncio.CancelledError:
        print("Sending username task cancelled.")

async def send_winner(writer):
    global win, side
    try:
        while True:
            await winner_available_event.wait()
            winner_available_event.clear()
            
            if win:
                data = {
                    "Winner": username,
                    "side": side
                }
                
                await send_json(data, writer)
    except asyncio.CancelledError:
        print("Sending username task cancelled.")

async def send_ballpos(writer):
    global ballposx
    global ballposy
    global ballside
    try:
        while True:
            await ballpos_available_event.wait()
            ballpos_available_event.clear()
            
            if ballposx:
                data = {
                    "ballposx": ballposx,
                    "ballposy": ballposy,
                    "ballside": ballside
                }
                
                await send_json(data, writer)
    except asyncio.CancelledError:
        print("Sending ball position task cancelled.")
        
async def receive_messages(reader):
    # asynchronously receive messages from the server
    global decoded_msg
    
    try:
        while True:
            response = await reader.read(1024)
            
            if response:
                decoded_msg = response.decode()
                print(f"Received: {decoded_msg}")
            else:
                print("Empty response from server.")
            
            await asyncio.sleep(0.05)
    except asyncio.CancelledError:
        print("Receiving messages task cancelled.")
            

# async def tcp_client():
#     """Handles asynchronous communication with the server."""
#     global strip_output, decoded_msg, total_rtt

#     reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
#     print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

#     try:
#         while True:
#             await strip_output_event.wait()  # Wait for new console output
#             strip_output_event.clear()  # Reset the event

#             if strip_output:
#                 message = strip_output
#                 processed_msg = message  # Extract hex if present
            

#                 #start_time = asyncio.get_event_loop().time()  # Start RTT timer
#                 writer.write(processed_msg.encode())
#                 await writer.drain()  # Ensure data is sent
                
#                 #print("[DEBUG] Waiting for response from server...")
#                 response = await reader.read(1024)  # Read up to 1024 bytes

#                 if response:
#                     decoded_msg = response.decode()  # Decode received data
#                     #print(f"[DEBUG] Raw response from server: {response}")
#                     print(f"{decoded_msg}")  # Print received message
#                 else:
#                     print("[Warning] Empty response from server.")

#             await asyncio.sleep(0.05)  # Allow time for next message
#     except asyncio.CancelledError:
#         print("TCP Client Task Cancelled.")
#     finally:
#         writer.close()
#         await writer.wait_closed()
#         print("Connection closed.")

async def tcp_client():
    #handles asynchronous communication with the server
    global writer
    
    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")
    
    send_task = asyncio.create_task(send_messages(writer))
    receive_task = asyncio.create_task(receive_messages(reader))
    username_task = asyncio.create_task(send_username(writer))
    
    try:
        await asyncio.gather(send_task, receive_task, username_task)
    except asyncio.CancelledError:
        print("TCP Client Task Cancelled.")
    finally:
        send_task.cancel()
        receive_task.cancel()
        await asyncio.gather(send_task, receive_task, username_task, return_exceptions=True)
        
        writer.close()
        await writer.wait_closed()
        print("Connection closed.")

async def main():
    # global username, side
    # username_available_event.clear()
    # username = input("Enter username: ")
    # side = input("Enter side (e.g., 'client' or 'server'): ")
    
    # # Signal that the username is available
    # username_available_event.set()
    
    """Main function to start both tasks concurrently."""
    nios_task = asyncio.create_task(stream_nios_console())
    tcp_task = asyncio.create_task(tcp_client())
    
    try:
        await asyncio.gather(nios_task, tcp_task)  # Run both concurrently
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        nios_task.cancel()
        tcp_task.cancel()
        await asyncio.gather(nios_task, tcp_task, return_exceptions=True)

if __name__ == "__main__":

    asyncio.run(main())