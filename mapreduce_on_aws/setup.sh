#!/bin/bash

chmod +x install_hadoop_spark.sh
chmod +x after_reboot.sh
chmod +x time_comparison.sh

chmod 600 /home/ubuntu/.ssh/ms_kp_pem.pem

sudo mv after_reboot.sh /var/lib/cloud/scripts/per-boot/

/home/ubuntu/install_hadoop_spark.sh