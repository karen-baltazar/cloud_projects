#!/bin/bash

if [ "$1" = "--after-reboot" ]; then
	# Install openjdk 8
	sudo apt install openjdk-8-jdk -y

	# Install openssh
	sudo apt install openssh-server openssh-client -y

	# Install ec2 tools
	sudo apt install amazon-ec2-utils

	# Download hadoop-3.3.6
	wget https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz -P ~/Downloads

	sudo tar zxvf ~/Downloads/hadoop-* -C /usr/local

	sudo mv /usr/local/hadoop-* /usr/local/hadoop

	# Download spark 3.5.0
	wget https://dlcdn.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz -P ~/Downloads

	sudo tar zxvf ~/Downloads/spark-* -C /usr/local

    sudo mv /usr/local/spark-* /usr/local/spark

	# Get the DNS Name
	DNS_NAME=`ec2-metadata --public-hostname`
	# Take the part after the semi colon
	DNS_NAME=${DNS_NAME##*:}
	# Trim the string
	DNS_NAME="${DNS_NAME#"${DNS_NAME%%[![:space:]]*}"}"

	# Get the private IP
	PRIVATE_IP=`ec2-metadata --local-ipv4`
	# Take the part after the semi colon
	PRIVATE_IP=${PRIVATE_IP##*:}
	# Trim the string
	PRIVATE_IP="${PRIVATE_IP#"${PRIVATE_IP%%[![:space:]]*}"}"
	
	# Declare some variables needed for the configuration later
	HADOOP_HOME=/usr/local/hadoop
	HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
	SPARK_HOME=/usr/local/spark
    SPARK_CONF_DIR=$SPARK_HOME/conf
	
	sudo sed -i 's\# export JAVA_HOME=.*\export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64\' $HADOOP_CONF_DIR/hadoop-env.sh

	sudo sed -i 's\# export HADOOP_CONF_DIR=.*\export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop\' $HADOOP_CONF_DIR/hadoop-env.sh	
	
	sudo sed -i "1 i\\$PRIVATE_IP hadoop" /etc/hosts


	# Configuration Starts

	sudo sed -i "s@<configuration>@<configuration>\n\t<property>\n\t\t<name>fs.defaultFS</name>\n\t\t<value>hdfs://$DNS_NAME:9000</value>\n\t</property>@" $HADOOP_CONF_DIR/core-site.xml

	sudo sed -i "s@<configuration>@<configuration>\n\t<property>\n\t\t<name>yarn.nodemanager.aux-services</name>\n\t\t<value>mapreduce_shuffle</value>\n\t</property>\n\t<property>\n\t\t<name>yarn.resourcemanager.hostname</name>\n\t\t<value>$DNS_NAME</value>\n\t</property>@" $HADOOP_CONF_DIR/yarn-site.xml

	sudo sed -i "s@<configuration>@<configuration>\n\t<property>\n\t\t<name>mapreduce.jobtracker.address</name>\n\t\t<value>$DNS_NAME:54311</value>\n\t</property>\n\t<property>\n\t\t<name>mapreduce.framework.name</name>\n\t\t<value>yarn</value>\n\t</property>\n\t<property>\n\t\t<name>yarn.app.mapreduce.am.env</name>\n\t\t<value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>\n\t</property>\n\t<property>\n\t\t<name>mapreduce.map.env</name>\n\t\t<value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>\n\t</property>\n\t<property>\n\t\t<name>mapreduce.reduce.env</name>\n\t\t<value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>\n\t</property>@" $HADOOP_CONF_DIR/mapred-site.xml

	sudo sed -i "s@<configuration>@<configuration>\n\t<property>\n\t\t<name>dfs.replication</name>\n\t\t<value>1</value>\n\t</property>\n\t<property>\n\t\t<name>dfs.namenode.name.dir</name>\n\t\t<value>file:///usr/local/hadoop/data/hdfs/namenode</value>\n\t</property>\n\t<property>\n\t\t<name>dfs.datanode.data.dir</name>\n\t\t<value>file:///usr/local/hadoop/data/hdfs/datanode</value>\n\t</property>@" $HADOOP_CONF_DIR/hdfs-site.xml

	# Create namenode and datanode directories
	sudo mkdir -p $HADOOP_HOME/data/hdfs/namenode
	sudo mkdir -p $HADOOP_HOME/data/hdfs/datanode

	# Change the owner
	sudo chown -R ubuntu $HADOOP_HOME

	# Create masters file
	cat > $HADOOP_HOME/masters <<-EOF
	hadoop

	EOF

	# Create slaves file
	cat > $HADOOP_HOME/slaves <<-EOF
	hadoop

	EOF

	# Create spark configuration directory
	sudo mkdir -p $SPARK_CONF_DIR

	# Configure Spark to use Hadoop HDFS
    echo "export HADOOP_CONF_DIR=$HADOOP_CONF_DIR" > $SPARK_CONF_DIR/spark-env.sh

    # Spark default settings (adjust as needed)
    cat <<EOF > $SPARK_CONF_DIR/spark-defaults.conf
    spark.master  yarn
    spark.eventLog.enabled  false
EOF

	# Configuration Ends

	sudo rm /var/lib/cloud/scripts/per-boot/after_reboot.sh
else
    # Ubuntu 22.04 LTS: disable the popup "Which service should be restarted ?"
	sudo sed -i "/#\$nrconf{restart} = 'i';/s/.*/\$nrconf{restart} = 'a';/" /etc/needrestart/needrestart.conf

	sudo apt update && sudo apt upgrade -y

	# Change the hostname to hadoop
	sudo sed -i 's/ip-.\+/hadoop/' /etc/hostname

	# configure the env variables
	HADOOP_HOME=/usr/local/hadoop
	HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
	SPARK_HOME=/usr/local/spark
    SPARK_CONF_DIR=$SPARK_HOME/conf

	cat >> ~/.bashrc << EOF
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_INSTALL=$HADOOP_HOME
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_CONF_DIR=/usr/local/hadoop/etc/hadoop
export HADOOP_HDFS_HOME=$HADOOP_HOME
export HADOOP_OPTS="$HADOOP_OPTS-Djava.library.path=$HADOOP_HOME/lib/native"
export YARN_HOME=$HADOOP_HOME
export HADOOP_COMMON_LIB_NATIVE_DIR=$HADOOP_HOME/lib/native
export SPARK_HOME=/usr/local/spark
export PATH=$PATH:$HADOOP_HOME/sbin:$HADOOP_HOME/bin:$SPARK_HOME/bin
EOF
	
	# add ssh key
	ssh-keygen -f ~/.ssh/id_rsa -t rsa -P ""
	cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

	# Reboot the machine for the changes to be effective
	sudo reboot
fi