#!/bin/bash

# Path to the scripts
db_scripts_path="db_scripts"
cloud_scripts_path="cloud_patterns"

# Step 1: Create AWS instances using aws_setup.py
echo "Step 1: Creating AWS instances..."
output=$(python3 aws_setup.py "$@")
KEY_NAME=$(echo "$output" | head -n 1)
DNS_NAMES=$(echo "$output" | tail -n +2)

# Step 1.5: Update private IPs in scripts
echo "Step 1.5: Updating private IPs in scripts..."
./update_config_ips.sh

# Step 2: Copy mysql_stand_alone.sh to the AWS instance
echo "Step 2: Copying mysql_stand_alone.sh to the AWS instance..."
STAND_ALONE_DNS=$(echo "$DNS_NAMES" | awk 'NR==1 {print $1}')
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $db_scripts_path/mysql_stand_alone.sh ubuntu@$STAND_ALONE_DNS:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $db_scripts_path/benchmark.sh ubuntu@$STAND_ALONE_DNS:/home/ubuntu

# Step 3: Copy master_setup.sh, slave_setup.sh, and benchmark.sh to the AWS instances for MySQL Cluster
echo "Step 3: Copying master_setup.sh, slave_setup.sh, and benchmark.sh to the AWS instances..."

# Extract DNS names for master and slave nodes
MASTER_DNS=$(echo "$DNS_NAMES" | awk 'NR==2 {print $1}')
SLAVE_DNS_NAMES=$(echo "$DNS_NAMES" | awk 'NR>=3 && NR<=5 {print $1}')

# Copy master_setup.sh and benchmark.sh to the master node
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $db_scripts_path/master_setup.sh ubuntu@$MASTER_DNS:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $db_scripts_path/benchmark.sh ubuntu@$MASTER_DNS:/home/ubuntu

# Copy slave_setup.sh to all slave nodes
for DNS in $SLAVE_DNS_NAMES; do
  sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $db_scripts_path/slave_setup.sh ubuntu@$DNS:/home/ubuntu
done

# Step 4: Copying setup files to the instances for Cloud Patterns
echo "Step 4: Copying setup files to the instances for Cloud Patterns..."

# Copy proxy_setup.py to the Proxy instance
PROXY_DNS=$(echo "$DNS_NAMES" | awk 'NR==6 {print $1}')
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $cloud_scripts_path/proxy_setup.py ubuntu@$PROXY_DNS:/home/ubuntu

# Copy gatekeeper_setup.py to the Gatekeeper instance
GATEKEEPER_DNS=$(echo "$DNS_NAMES" | awk 'NR==7 {print $1}')
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $cloud_scripts_path/gatekeeper_setup.py ubuntu@$GATEKEEPER_DNS:/home/ubuntu

# Copy trusted_host_setup.py to the Trusted Host instance
TRUSTED_HOST_DNS=$(echo "$DNS_NAMES" | awk 'NR==8 {print $1}')
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $cloud_scripts_path/trusted_host_setup.py ubuntu@$TRUSTED_HOST_DNS:/home/ubuntu

echo "Automation script completed!"