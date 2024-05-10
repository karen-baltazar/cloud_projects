#!/bin/bash

# Download and configure Sakila database
wget https://downloads.mysql.com/docs/sakila-db.tar.gz
tar -xzvf sakila-db.tar.gz
cd sakila-db

# Load Sakila schema and data into MySQL
sudo mysql -u root < sakila-schema.sql
sudo mysql -u root < sakila-data.sql

# Install Sysbench and run benchmark
sudo apt-get install -y sysbench
sudo sysbench oltp_read_write --table-size=100000 --mysql-db=sakila --mysql-user=root prepare
sudo sysbench oltp_read_write --table-size=100000 --threads=6 --max-time=60 --max-requests=0 --mysql-db=sakila --mysql-user=root run > /home/ubuntu/results.txt
sudo sysbench oltp_read_write --mysql-db=sakila --mysql-user=root --my-sql-password=root cleanup