import sys
import random
import mysql.connector
from ping3 import ping, verbose_ping

# Configuration data [replace with your own values]
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
                for row in rows:
                    print(row)
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

def execute_direct_hit():
    print("Direct Hit Implementation...")

    # Forward the query to the master node
    query = "SELECT * FROM inventory LIMIT 5;"
    forward_to_node(mysql_master_ip, query)

def execute_random():
    print("Random Implementation...")

    # Randomly select an IP from the slave nodes
    random_slave_ip = random.choice(mysql_slave_ips)
    
    # Forward the query to the randomly selected node
    query = "DELETE FROM film ORDER BY film_id ASC LIMIT 1;"
    forward_to_node(random_slave_ip, query)

def execute_customized():
    print("Customized Implementation...")

    # Measure ping times for each server and find the server with the lowest ping time
    ping_times = {ip: measure_ping(ip) for ip in [mysql_master_ip] + mysql_slave_ips}
    best_ip = min(ping_times, key=ping_times.get)

    # Forward the query to the server with the lowest ping time
    query = "INSERT INTO language (name) VALUES ('Esperanto');"
    forward_to_node(best_ip, query)

def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python3 proxy_setup.py <implementation>")
        sys.exit(1)

    implementation = sys.argv[1]

    # Specific actions for the selected implementation
    if implementation == "direct_hit":
        execute_direct_hit()
    elif implementation == "random":
        execute_random()
    elif implementation == "customized":
        execute_customized()
    else:
        print(f"Unknown implementation: {implementation}")
        sys.exit(1)

if __name__ == "__main__":
    main()