#!/bin/bash

# Read private IP addresses from the file private_ips.txt
private_ip_addresses=($(cat private_ips.txt))

# Path to the scripts
db_scripts_path="db_scripts"
cloud_scripts_path="cloud_patterns"

# Replace ip addresses in the master_setup.sh script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_1_private_ip>/${private_ip_addresses[1]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_2_private_ip>/${private_ip_addresses[2]}/g" "${db_scripts_path}/master_setup.sh"
sed -i "s/<data_node_3_private_ip>/${private_ip_addresses[3]}/g" "${db_scripts_path}/master_setup.sh"

# Replace <master_private_ip> in the slave_setup.sh script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" "${db_scripts_path}/slave_setup.sh"

# Replace ip addresses in the proxy_setup.py script
sed -i "s/<master_private_ip>/${private_ip_addresses[0]}/g" "${cloud_scripts_path}/proxy_setup.sh"
sed -i "s/<data_node_1_private_ip>/${private_ip_addresses[1]}/g" "${cloud_scripts_path}/proxy_setup.sh"
sed -i "s/<data_node_2_private_ip>/${private_ip_addresses[2]}/g" "${cloud_scripts_path}/proxy_setup.sh"
sed -i "s/<data_node_3_private_ip>/${private_ip_addresses[3]}/g" "${cloud_scripts_path}/proxy_setup.sh"
sed -i "s/<proxy_private_ip>/${private_ip_addresses[4]}/g" "${cloud_scripts_path}/proxy_setup.sh"

# Replace ip addresses in the gatekeeper_setup.py script
sed -i "s/<trusted_host_private_ip>/${private_ip_addresses[6]}/g" "${cloud_scripts_path}/gatekeeper_setup.sh"

# Replace ip addresses in the trusted_host_setup.py script
sed -i "s/<proxy_private_ip>/${private_ip_addresses[4]}/g" "${cloud_scripts_path}/trusted_host_setup.sh"
sed -i "s/<trusted_host_private_ip>/${private_ip_addresses[6]}/g" "${cloud_scripts_path}/trusted_host_setup.sh"