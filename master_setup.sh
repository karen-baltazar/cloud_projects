#!/bin/bash

# Install dependencies
sudo apt-get update
sudo apt-get install libncurses5 libaio1 libmecab2 -y

# Download and install the MySQL Cluster Manager, ndb_mgmd
cd /home/ubuntu
sudo wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-management-server_7.6.6-1ubuntu18.04_amd64.deb

# Create the /var/lib/mysql-cluster/config.ini file for the cluster configuration  
sudo mkdir /var/lib/mysql-cluster
echo "
[ndbd default]
NoOfReplicas=3	

[ndb_mgmd]
hostname=<master_private_dns>
datadir=/var/lib/mysql-cluster 	

[ndbd]
hostname=<data_node_1_private_dns>
NodeId=2			
datadir=/usr/local/mysql/data

[ndbd]
hostname=<data_node_2_private_dns>
NodeId=3			
datadir=/usr/local/mysql/data

[ndbd]
hostname=<data_node_3_private_dns>
NodeId=4			
datadir=/usr/local/mysql/data

[mysqld]
hostname=<master_private_dns>
" > /var/lib/mysql-cluster/config.ini

# Add the instructions for systemd to start, stop, and restart ndb_mgmd
sudo bash -c 'cat > /etc/systemd/system/ndb_mgmd.service << EOF
[Unit]
Description=MySQL NDB Cluster Management Server
After=network.target auditd.service

[Service]
Type=forking
ExecStart=/usr/sbin/ndb_mgmd -f /var/lib/mysql-cluster/config.ini
ExecReload=/bin/kill -HUP $MAINPID
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF'

# Reload systemd manager, enable ndb_mgmd and start ndb_mgmd
sudo systemctl daemon-reload
sudo systemctl enable ndb_mgmd
sudo systemctl start ndb_mgmd

# Download MySQL Server
sudo wget https://dev.mysql.com/get/Downloads/MySQL-Cluster-7.6/mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar
sudo mkdir install
sudo tar -xvf mysql-cluster_7.6.6-1ubuntu18.04_amd64.deb-bundle.tar -C install/
cd install

# Install MySQL Server
sudo dpkg -i mysql-common_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-cluster-community-client_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-client_7.6.6-1ubuntu18.04_amd64.deb

# Configure installation to avoid using MySQL prompt
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/root-pass password root'
sudo debconf-set-selections <<< 'mysql-cluster-community-server_7.6.6 mysql-cluster-community-server/re-root-pass password root'

# Install the rest of the packages
sudo dpkg -i mysql-cluster-community-server_7.6.6-1ubuntu18.04_amd64.deb
sudo dpkg -i mysql-server_7.6.6-1ubuntu18.04_amd64.deb

# Configure client to connect to the master node
echo "
[mysqld]
ndbcluster                   

[mysql_cluster]
ndb-connectstring=<master_private_dns>
" > /etc/mysql/my.cnf

# Restart MySQL Server
sudo systemctl restart mysql
sudo systemctl enable mysql