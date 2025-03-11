import asyncio
from collections import deque

# Server details
SERVER_HOST = "18.130.232.65"
SERVER_PORT = 12000
NIOS_CMD_SHELL_BAT = "C:/intelFPGA_lite/18.1/nios2eds/Nios_II_Command_Shell.bat"

# RTT Tracking
# window_size = 500
# rtt_window = deque(maxlen=window_size)
# total_rtt = 0

# Shared Variables
strip_output = None
decoded_msg = None
strip_output_event = asyncio.Event()  # Async event for signaling new messages


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

async def tcp_client():
    """Handles asynchronous communication with the server."""
    global strip_output, decoded_msg, total_rtt

    reader, writer = await asyncio.open_connection(SERVER_HOST, SERVER_PORT)
    print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            await strip_output_event.wait()  # Wait for new console output
            strip_output_event.clear()  # Reset the event

            if strip_output:
                message = strip_output
                processed_msg = message  # Extract hex if present
            

                #start_time = asyncio.get_event_loop().time()  # Start RTT timer
                writer.write(processed_msg.encode())
                await writer.drain()  # Ensure data is sent
                
                #print("[DEBUG] Waiting for response from server...")
                response = await reader.read(1024)  # Read up to 1024 bytes

                if response:
                    decoded_msg = response.decode()  # Decode received data
                    #print(f"[DEBUG] Raw response from server: {response}")
                    print(f"{decoded_msg}")  # Print received message
                else:
                    print("[Warning] Empty response from server.")

            await asyncio.sleep(0.05)  # Allow time for next message
    except asyncio.CancelledError:
        print("TCP Client Task Cancelled.")
    finally:
        writer.close()
        await writer.wait_closed()
        print("Connection closed.")

async def main():
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
