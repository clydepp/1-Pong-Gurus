import socket
import threading
import json 

# Server settings
server_port = 12000
clients = []  # List of connected clients

print("Starting TCP server...")

# Create and bind the server socket
welcome_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
welcome_socket.bind(('0.0.0.0', server_port))
welcome_socket.listen(5)  # Allow up to 5 clients to queue

def handle_client(client_socket, addr):
    """Handles communication with a single client."""
    global clients

    print(f"New client connected: {addr}")
    clients.append(client_socket)

    try:
        while True:
            cmsg = client_socket.recv(1024)
            if not cmsg:
                break  # Client disconnected

            cmsg = cmsg.decode().strip()
            print(f"Received from {addr}: {cmsg}")

            try: 
                data = json.loads(cmsg)
                #print(f"JSON data: {data}")
                
                if isinstance(data, dict) and "username" in data and "side" in data: # check if data is username and side
                    username = data.get("username")
                    side = data.get("side")
                    print(f"Extracted: Username: {username}, Side: {side}")
                    broadcast(cmsg, client_socket)
                
                else:
                    print("Invalid JSON data.")
            
            except json.JSONDecodeError:
                print("Not Json data.")
            # Broadcast message to all other clients
            broadcast(cmsg, client_socket)

    except ConnectionResetError:
        print(f"Client {addr} forcibly closed the connection.")

    finally:
        print(f"Client {addr} disconnected.")
        clients.remove(client_socket)
        client_socket.close()

def broadcast(message, sender_socket):
    """Sends a message to all clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                # Remove unresponsive clients
                clients.remove(client)

# Main server loop
print(f"Server running on port {server_port}...")

while True:
    print("Waiting for a new client...")
    client_socket, client_addr = welcome_socket.accept()
    
    # Start a new thread for each client
    threading.Thread(target=handle_client, args=(client_socket, client_addr), daemon=True).start()
