import matplotlib.pyplot as plt
import numpy as np
import re
import os

def get_execution_times_from_file(filename):
    # Open file containing execution times
    with open(filename, 'r') as file:
        data = file.read()

    # Process data and extract execution times for each dataset
    dataset_execution_times = {}
    for line in data.strip().split('\n'):
        if line.startswith('Dataset'):
            current_dataset = int(re.search(r'\d+', line).group())  # Extract dataset number
        elif line.startswith('real'):
            time_match = re.search(r'(\d+)m([\d.]+)s', line)  # regex to extract execution time as a string
            minutes = round(float(time_match.group(1)), 2)  # Extract number of minutes
            seconds = round(float(time_match.group(2)), 2)  # Extract number of seconds
            exec_time_in_seconds = seconds + 60 * minutes  # compute execution time
            if exec_time_in_seconds:
                dataset_execution_times.setdefault(current_dataset, []).append(exec_time_in_seconds)
    
    return dataset_execution_times

def plot_specific_graph(dataset_num, dataset_execution_times, framework_used):
    x_axis = np.arange(1, len(dataset_execution_times) + 1)
    
    # configure plot
    plt.plot(x_axis, dataset_execution_times)

    plt.title(f'Execution Time of {framework_used} on Dataset {dataset_num}')
    plt.xlabel('Run Number')
    plt.ylabel('Execution Time (s)')

    plt.scatter(x_axis, dataset_execution_times)

    plt.xticks(x_axis)
    plt.ylim(0, max(dataset_execution_times) + 5)

    # Annotate data points on the graph 
    for i in range(3): 
        plt.annotate(dataset_execution_times[i], (x_axis[i], dataset_execution_times[i] + 0.5))

    # Save file
    plt.savefig(f'graphs/{framework_used}_time_dataset_{dataset_num}.png')
    plt.clf()

    return

def get_average_times(execution_times_dict):
    # compute the average time for each dataset
    average_times = []
    for dataset, times in execution_times_dict.items():
        average_times.append(np.round(np.mean(times), 2))
    
    return average_times

def plot_average_graph(hadoop_execution_times, spark_execution_times):
    x_axis = np.arange(1,10)
    
    # configure plot
    plt.plot(x_axis, hadoop_execution_times, label = "Hadoop")
    plt.plot(x_axis, spark_execution_times, label = "Spark")

    plt.title('Average Execution Times for Each Dataset')
    plt.xlabel('Dataset Number')
    plt.ylabel('Average Execution Time (s)')

    plt.scatter(x_axis, hadoop_execution_times)
    plt.scatter(x_axis, spark_execution_times)
    
    plt.xticks(x_axis)
    plt.legend()

    # Annotate data points on the graph 
    for i in range(9): 
        plt.annotate(hadoop_execution_times[i], (x_axis[i], hadoop_execution_times[i] + 0.5))
        plt.annotate(spark_execution_times[i], (x_axis[i], spark_execution_times[i] + 0.5))

    # Save file
    plt.savefig('graphs/average_times.png')
    plt.clf()

def main():
    # Create a graphs folder if it doesn't already exist
    if not os.path.exists('graphs'):
        os.makedirs('graphs')

    # Process the files to get the execution times in a dictionary
    exec_times_hadoop = get_execution_times_from_file("hadoop_time.txt")
    exec_times_spark = get_execution_times_from_file("spark_time.txt")

    # Plot a graph for each dataset and framework 
    for dataset_num in range(1, len(exec_times_hadoop) + 1):
        plot_specific_graph(dataset_num, exec_times_hadoop[dataset_num], "Hadoop")
        plot_specific_graph(dataset_num, exec_times_spark[dataset_num], "Spark")

    # Get the average values for each dataset
    hadoop_average_times = get_average_times(exec_times_hadoop)
    spark_average_times = get_average_times(exec_times_spark)

    # Plot the average graph which compares Hadoop and Spark
    plot_average_graph(hadoop_average_times, spark_average_times)
    return

if __name__ == "__main__":
    main()