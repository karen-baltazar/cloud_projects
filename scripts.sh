#!/bin/bash

# Step 1: Create AWS instances using aws_setup.py
echo "Step 1: Creating AWS instances..."
output=$(python3 aws_setup.py "$@")
KEY_NAME=$(echo "$output" | head -n 1)
DNS_NAMES=$(echo "$output" | tail -n +2)

# Step 2: Copy mysql_stand_alone.sh to the AWS instance
echo "Step 2: Copying mysql_stand_alone.sh to the AWS instance..."
DNS_NAME=$(echo "$DNS_NAMES" | head -n 1)
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME mysql_stand_alone.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME benchmark.sh ubuntu@$DNS_NAME:/home/ubuntu

# Step 3: Copy master.sh, slave.sh, and benchmark.sh to the AWS instances for MySQL Cluster
echo "Step 3: Copying master.sh, slave.sh, and benchmark.sh to the AWS instances..."
for DNS in $(echo "$DNS_NAMES" | tail -n +2); do
  sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME master.sh ubuntu@$DNS:/home/ubuntu
  sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME slave.sh ubuntu@$DNS:/home/ubuntu
  sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME benchmark.sh ubuntu@$DNS:/home/ubuntu
done

# Step 4: Copying proxy_setup.py to the Proxy instance
echo "Step 4: Copying proxy_setup.py to the Proxy instance..."
PROXY_DNS_NAME=$(echo "$output" | tail -n 1)
sudo scp -o StrictHostKeyChecking=no -i $PROXY_KEY_NAME proxy_setup.py ubuntu@$PROXY_DNS_NAME:/home/ubuntu

echo "Automation script completed!"