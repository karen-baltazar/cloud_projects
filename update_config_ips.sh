#!/bin/bash

# Read private IP addresses from the file private_ips.txt
private_ip_addresses=($(cat private_ips.txt))

# Path to the db_scripts folder
db_scripts_path="db_scripts"

# Replace ip addresses in the master_setup.sh script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_1_private_ip>/${private_ip_addresses[1]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_2_private_ip>/${private_ip_addresses[2]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_3_private_ip>/${private_ip_addresses[3]}/g" "${db_scripts_path}/master_setup.sh"

# Replace ip addresses in the proxy_setup.py script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" proxy_setup.py
sed -i "s/<data_node_1_private_ip>/${private_ip_addresses[1]}/g" proxy_setup.py
sed -i "s/<data_node_2_private_ip>/${private_ip_addresses[2]}/g" proxy_setup.py
sed -i "s/<data_node_3_private_ip>/${private_ip_addresses[3]}/g" proxy_setup.py

# Replace <master_private_ip> in the slave_setup.sh script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" "${db_scripts_path}/slave_setup.sh"