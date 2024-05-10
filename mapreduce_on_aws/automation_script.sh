#!/bin/bash

# Configure AWS Cluster
output=$(python3 aws_setup.py "$@")
DNS_NAME=${output#*:}
KEY_NAME=${output%:*}

# Create config file
cat > ~/.ssh/config << EOF
Host hadoop
    HostName $DNS_NAME
    User ubuntu
    IdentityFile ~/.ssh/$KEY_NAME

EOF

# Copy pem key to .ssh
cp $KEY_NAME ~/.ssh

sed -i "s@chmod 600 /home/ubuntu/.ssh/.*@chmod 600 /home/ubuntu/.ssh/$KEY_NAME@" setup.sh

sleep 1m

sed -i -e 's/\r$//' install_hadoop_spark.sh
sed -i -e 's/\r$//' after_reboot.sh
sed -i -e 's/\r$//' setup.sh
sed -i -e 's/\r$//' time_comparison.sh

sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME $KEY_NAME ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/config ubuntu@$DNS_NAME:~/.ssh
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME ~/.ssh/*.pem ubuntu@$DNS_NAME:~/.ssh

sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME after_reboot.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME install_hadoop_spark.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME setup.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME time_comparison.sh ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME wordcount_spark.py ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME comparison.py ubuntu@$DNS_NAME:/home/ubuntu
sudo scp -o StrictHostKeyChecking=no -i $KEY_NAME -r datasets ubuntu@$DNS_NAME:/home/ubuntu

sudo rm ~/.ssh/config
sudo rm ~/.ssh/$KEY_NAME