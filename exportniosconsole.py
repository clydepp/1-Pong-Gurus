import subprocess

# Path to the Nios II Command Shell batch file
NIOS_CMD_SHELL_BAT = "C:/intelFPGA_lite/18.1/nios2eds/Nios_II_Command_Shell.bat"

def stream_nios_console():
    """
    Continuously reads and outputs the contents of the Nios II console.
    """
    # Start the Nios II Command Shell and run nios2-terminal
    process = subprocess.Popen(
        [NIOS_CMD_SHELL_BAT, "nios2-terminal"],  # Run nios2-terminal directly
        stdout=subprocess.PIPE,  # Capture stdout
        stderr=subprocess.PIPE,  # Capture stderr
        text=True,  # Use text mode for easier string handling
    )

    print("Streaming Nios II console output... Press Ctrl+C to stop.")
    try:
        while True:
            # Read a line from the console output
            output = process.stdout.readline()
            if output:
                print(output.strip())  # Print the output to the console
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

if __name__ == "__main__":
    main()