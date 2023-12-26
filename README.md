# LOG8415 - Final Project
## 1. Benchmarking MySQL stand-alone vs. MySQL Cluster

To conduct benchmarking after executing `scripts.sh`, follow these steps:

### Stand-alone Environment:
1. Connect to the stand-alone instance via SSH.
2. Execute `mysql_stand_alone.sh` on the corresponding instance.
3. Run `benchmark.sh` to perform performance tests and save the results to `/home/ubuntu/results.txt`.
4. To view the results, navigate to the `/home/ubuntu/` directory and open the file using a text editor such as `nano` or `cat`.

### Cluster Environment:
1. Connect to the master node instance via SSH.
2. Execute `master_setup.sh` on the master node.
3. Connect to each slave node via SSH and run `slave_setup.sh`.
4. Reconnect to the master node and run `benchmark.sh` to perform performance tests. The results will be saved in `/home/ubuntu/results.txt`.
5. To view the results, navigate to the `/home/ubuntu/` directory and open the file using a text editor such as `nano` or `cat`.

For more information, see the attached report in the repository.
