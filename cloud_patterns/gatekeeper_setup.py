import socket
import sys

# Configuration data [replace with your own values]
trusted_host_ip = "<trusted_host_private_ip>"
trusted_host_port = 50000 # This is the port that the Trusted Host is listening on

def send_query(query):
    # Connect to Trusted Host and send the query
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((trusted_host_ip, trusted_host_port))
        client_socket.sendall(query.encode("utf-8"))
        print(f"Query sent to Trusted Host: {query}")

def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 gatekeeper_setup.py <query>")
        sys.exit(1)

    incoming_query = sys.argv[1]

    # Forward the incoming query to the Trusted Host
    send_query(incoming_query)

if __name__ == "__main__":
    main()
