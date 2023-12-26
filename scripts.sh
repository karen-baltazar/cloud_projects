#!/bin/bash

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
DNS_NAME=$(echo "$DNS_NAMES" | head -n 1)
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME db_scripts/mysql_stand_alone.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME db_scripts/benchmark.sh ubuntu@$DNS_NAME:/home/ubuntu

# Step 3: Copy master_setup.sh, slave_setup.sh, and benchmark.sh to the AWS instances for MySQL Cluster
echo "Step 3: Copying master_setup.sh, slave_setup.sh, and benchmark.sh to the AWS instances..."

# Extract DNS names for master and slave nodes
MASTER_DNS=$(echo "$DNS_NAMES" | awk 'NR==2 {print $1}')
SLAVE_DNS_NAMES=$(echo "$DNS_NAMES" | awk 'NR>=3 && NR<=5 {print $1}')

# Copy master_setup.sh and benchmark.sh to the master node
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME db_scripts/master_setup.sh ubuntu@$MASTER_DNS:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME db_scripts/benchmark.sh ubuntu@$MASTER_DNS:/home/ubuntu

# Copy slave_setup.sh to all slave nodes
for DNS in $SLAVE_DNS_NAMES; do
  sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME db_scripts/slave_setup.sh ubuntu@$DNS:/home/ubuntu
done

# Step 4: Copying proxy_setup.py to the Proxy instance
echo "Step 4: Copying proxy_setup.py to the Proxy instance..."
PROXY_DNS_NAME=$(echo "$output" | tail -n 1)
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME proxy_setup.py ubuntu@$PROXY_DNS_NAME:/home/ubuntu

echo "Automation script completed!"