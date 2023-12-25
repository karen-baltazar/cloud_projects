#!/bin/bash

# Common setup
sudo apt-get update
sudo apt-get -y install libncurses5

mkdir -p /opt/mysqlcluster/home
cd /opt/mysqlcluster/home
wget http://dev.mysql.com/get/Downloads/MySQL-Cluster-7.2/mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
tar xvf mysql-cluster-gpl-7.2.1-linux2.6-x86_64.tar.gz
ln -s mysql-cluster-gpl-7.2.1-linux2.6-x86_64 mysqlc

echo 'export MYSQLC_HOME=/opt/mysqlcluster/home/mysqlc' > /etc/profile.d/mysqlc.sh
echo 'export PATH=$MYSQLC_HOME/bin:$PATH' >> /etc/profile.d/mysqlc.sh
source /etc/profile.d/mysqlc.sh

# Create directories for the cluster
sudo mkdir -p /opt/mysqlcluster/deploy
cd /opt/mysqlcluster/deploy
sudo mkdir conf
sudo mkdir mysqld_data
sudo mkdir ndb_data
cd conf

# Create configuration files
sudo tee my.cnf <<EOL
[mysqld]
ndbcluster
datadir=/opt/mysqlcluster/deploy/mysqld_data
basedir=/opt/mysqlcluster/home/mysqlc
port=3306
EOL

sudo tee config.ini <<EOL
[ndb_mgmd]
hostname=<master_private_dns>
datadir=/opt/mysqlcluster/deploy/ndb_data
nodeid=1

[ndbd default]
noofreplicas=2
datadir=/opt/mysqlcluster/deploy/ndb_data

[ndbd]
hostname=<data_node_1_private_dns>
nodeid=2

[ndbd]
hostname=<data_node_2_private_dns>
nodeid=3

[ndbd]
hostname=<data_node_3_private_dns>
nodeid=4

[mysqld]
nodeid=50
EOL

# Initialize the database
sudo /opt/mysqlcluster/home/mysqlc/scripts/mysql_install_db --no-defaults --datadir=/opt/mysqlcluster/deploy/mysqld_data

# Start management node
sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgmd -f /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf

# Start data nodes
sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c <master_private_dns>:1186
sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c <data_node_1_private_dns>:1186
sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c <data_node_2_private_dns>:1186
sudo /opt/mysqlcluster/home/mysqlc/bin/ndbd -c <data_node_3_private_dns>:1186

# Check cluster status
sudo /opt/mysqlcluster/home/mysqlc/bin/ndb_mgm -e show

# Start SQL node
sudo /opt/mysqlcluster/home/mysqlc/bin/mysqld --defaults-file=/opt/mysqlcluster/deploy/conf/my.cnf --user=root &

# Wait for MySQL server to be ready
echo "Waiting for MySQL server to be ready..."
while ! sudo /opt/mysqlcluster/home/mysqlc/bin/mysqladmin --socket=/opt/mysqlcluster/deploy/mysqld_data/mysql.sock ping &> /dev/null ; do sleep 1; done

# Secure MySQL installation
sudo /opt/mysqlcluster/home/mysqlc/bin/mysql_secure_installation
