# import socket
# print("We're in tcp server...");

# #select a server port
# server_port = 12000
# #create a welcoming socket
# welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# #bind the server to the localhost at port server_port
# welcome_socket.bind(('0.0.0.0',server_port))

# welcome_socket.listen(1)

# #ready message
# print('Server running on port ', server_port)

# #Now the main server loop
# while True:
    
    # connection_socket, caddr = welcome_socket.accept()
    # #notice recv and send instead of recvto and sendto
    # while True:
        # print(f"hi1")
        
        # print(f"hi2")
        # cmsg = connection_socket.recv(1024)
        # cmsg = cmsg.decode()
        # if(cmsg.isalnum() == False):
            # cmsg = "Not alphanumeric.";
        # else:
            # cmsg = "Alphanumeric";
        # connection_socket.send(cmsg.encode())
        # print(f"hi3")

import socket
import time

print("We're in TCP server...")

# Select a server port
server_port = 12000

# Create a welcoming socket
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcome_socket.bind(('0.0.0.0', server_port))

# Start listening for incoming connections
welcome_socket.listen(5)  # Allow up to 5 clients to queue

print(f"Server running on port {server_port}...")

while True:  # Main server loop: Accept new clients
    print("Waiting for a new client...")  # Debugging message
    connection_socket, caddr = welcome_socket.accept()
    print(f"Connected to {caddr}")
    
    #start_time = time.time()  # Record the start time

    while True:  # Inner loop: Handle multiple messages from this client
        try:
            
            # elapsed_time = time.time() - start_time
            # if elapsed_time < 3:
                # print(f"Ignoring input (first 3 seconds)")
                # continue  # Skip processing and go back to receiving data
                
            print("Waiting for message...")
            cmsg = connection_socket.recv(1024)
            if not cmsg:  # If the client disconnects, exit the loop
                print(f"Client {caddr} disconnected.")
                break

            # Process message
            cmsg = cmsg.decode().strip()
            response = "Alphanumeric" if cmsg.isalnum() else "Not alphanumeric."
            
            # Send response back to the client
            connection_socket.send(response.encode())
            print(f"Processed message: {cmsg} -> Response: {response}")

        except ConnectionResetError:
            print(f"Client {caddr} forcibly closed the connection.")
            break

    connection_socket.close()  # Close connection before accepting a new client
    print("Ready for a new client...")  # Debugging message
