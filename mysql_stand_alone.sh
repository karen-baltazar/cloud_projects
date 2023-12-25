#!/bin/bash

# Update package list
sudo apt-get update

# Install MySQL server
sudo apt-get install -y mysql-server

# Start MySQL service
sudo systemctl start mysql.service

# Enable MySQL service to start on boot
sudo systemctl enable mysql.service