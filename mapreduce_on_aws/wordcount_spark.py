from pyspark import SparkContext, SparkConf
import time

# Start the timer
start_time = time.time()

# Create a SparkContext
conf = SparkConf().setMaster("local[*]").setAppName("WordCount")
sc = SparkContext(conf=conf)

# Load all files in the input directory
input_directory = "WordCount/input"
files = sc.wholeTextFiles(input_directory)

# Counting the occurences of each word
counts = files.flatMap(lambda file_content: file_content[1].split(" ")).map(lambda word: (word, 1)).reduceByKey(lambda a, b: a + b)

# Save the results to an output file
output_directory = "WordCount/output"
counts.saveAsTextFile(output_directory)

# Stop the SparkContext
sc.stop()

# Stop the timer
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time

# Print the execution time
print(f"Execution time: {execution_time} seconds")
