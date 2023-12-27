import sys
import random
import re
import mysql.connector
from ping3 import ping, verbose_ping

# Configuration data [replace with your own values]
proxy_ip = "<proxy_private_ip>"
proxy_port = 60000  # This is the port that the Proxy is listening on
mysql_user = "root"
mysql_password = "root"
database_name = 'sakila'
mysql_master_ip = "<master_private_ip>"
mysql_slave_ips = ["<data_node_1_private_ip>", "<data_node_2_private_ip>", "<data_node_3_private_ip>"]

def connect_to_mysql(config, attempts=3):
    # Function to connect to MySQL with retry
    for _ in range(attempts):
        try:
            cnx = mysql.connector.connect(**config)
            return cnx
        except mysql.connector.Error as err:
            print(f"Error: {err}")
    return None

def forward_to_node(node_ip, query):
    # Forward the query to the MySQL node and display the results
    config = {
        "host": node_ip,
        "user": mysql_user,
        "password": mysql_password,
        "database": database_name,
    }

    cnx = connect_to_mysql(config)
    if cnx and cnx.is_connected():
        try:
            with cnx.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
            print(f"Query executed successfully on host {node_ip}")
        except mysql.connector.Error as err:
            print(f"Error executing query: {err}")
        finally:
            cnx.close()
    else:
        print(f"Could not connect to host {node_ip}")

def measure_ping(ip):
    # Measure ping time to the provided IP
    try:
        response_time = ping(ip)
        return response_time
    except Exception as e:
        print(f"Error measuring ping to {ip}: {e}")
        return float('inf')

def execute_direct_hit(query):
    print("Direct Hit Implementation...")

    # Forward the query to the master node
    forward_to_node(mysql_master_ip, query)

def execute_random(query):
    print("Random Implementation...")

     # Forward the query to the randomly selected node
    random_slave_ip = random.choice(mysql_slave_ips)
    forward_to_node(random_slave_ip, query)

def execute_customized(query):
    print("Customized Implementation...")

    # Forward the query to the server with the lowest ping time
    ping_times = {ip: measure_ping(ip) for ip in [mysql_master_ip] + mysql_slave_ips}
    best_ip = min(ping_times, key=ping_times.get)
    forward_to_node(best_ip, query)

def is_write_query(query):
    # Check if the query is a write operation (INSERT, UPDATE, DELETE)
    return re.match(r'\b(INSERT|UPDATE|DELETE)\b', query, re.IGNORECASE) is not None

def execute_query(query):
    # Determine which MySQL node to send the query to based on the type of operation
    if is_write_query(query):
        execute_direct_hit(query)
    else:
        execute_customized(query)

def main():
     # Listen for incoming connections and receive the query
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((proxy_ip, proxy_port))
        server_socket.listen()
        print("Proxy listening for connections...")
        connection, address = server_socket.accept()
        with connection:
            print(f"Connected to: {address}")
            data = connection.recv(1024)
            if not data:
                print("No query received.")
                return

            query = data.decode("utf-8")

            # Forward the query to the appropriate MySQL node and get the results
            results = execute_query(query)

            # Send the results back to the client
            connection.sendall(str(results).encode("utf-8"))

if __name__ == "__main__":
    main()