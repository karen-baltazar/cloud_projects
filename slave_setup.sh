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

# Configuration for ndbd (data node)
echo "[ndbd]" > config.ini
echo "hostname=<data_node_private_dns>" >> config.ini
echo "nodeid=2" >> config.ini

# Start the data node
/opt/mysqlcluster/home/mysqlc/bin/ndbd -c /opt/mysqlcluster/deploy/conf/config.ini --initial --configdir=/opt/mysqlcluster/deploy/conf/

# Check status
/opt/mysqlcluster/home/mysqlc/bin/ndb_mgm -e show