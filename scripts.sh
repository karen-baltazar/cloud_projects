#!/bin/bash

# Step 1: Run aws_setup.py to configure the AWS instance
echo "Step 1: Configuring AWS instance..."
output=$(python3 aws_setup.py "$@")
KEY_NAME=$(echo "$output" | head -n 1)
DNS_NAMES=$(echo "$output" | tail -n +2)

# Step 2: Copy mysql_stand_alone.sh to the AWS instance
echo "Step 2: Configuring MySQL Stand-Alone..."
DNS_NAME=$(echo "$DNS_NAMES" | head -n 1)
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME mysql_stand_alone.sh ubuntu@$DNS_NAME:/home/ubuntu

echo "Automation script completed!"