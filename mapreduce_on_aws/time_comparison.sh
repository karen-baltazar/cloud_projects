# launch the hadoop cluster
hdfs namenode -format
$HADOOP_HOME/sbin/start-dfs.sh
$HADOOP_HOME/sbin/start-yarn.sh
$HADOOP_HOME/sbin/mr-jobhistory-daemon.sh start historyserver

# create the input folder and add the datasets to it
hdfs dfs -mkdir -p WordCount/input
hdfs dfs -put datasets/*.txt WordCount/input

touch hadoop_time.txt
touch spark_time.txt

for dataset in {1..9}; do
# for each data set
    for i in {1..3}; do
    # for each execution
        
        # Run Hadoop wordcount program and save the execution time
        echo "Dataset $dataset, execution $i" >> hadoop_time.txt
        (time hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-3.3.6.jar wordcount WordCount/input/text{$dataset}.txt WordCount/output) 2>&1 | grep real >> hadoop_time.txt
        
        # Delete the output folder after each execution
        hdfs dfs -rm -r WordCount/output
    done
done

for dataset in {1..9}; do
    # For each dataset
    for i in {1..3}; do
        # For each execution

        # Run Spark wordcount program and save the execution time
        echo "Dataset $dataset, execution $i" >> spark_time.txt
        { time spark-submit \
            --master local \
            --name "WordCount" \
            --executor-memory 1g \
            --driver-memory 1g \
            --class org.apache.spark.examples.JavaWordCount \
            examples/jars/spark-examples_2.12-3.2.0.jar \
            hdfs://localhost:9000/user/azureuser/WordCount/input/text${dataset}.txt ; } 2>&1 | grep real >> spark_time.txt
    done
done
