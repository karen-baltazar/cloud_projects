import os
import time
import logging
from threaded_req import ThreadedRequest
from cloudwatch import Widgets

def benchmark(ec2_url):
    cluster_paths = [ '/cluster1', '/cluster2' ]

    # Run the threaded requests for each path
    for path in cluster_paths:
        cluster = ec2_url + path
        th_req = ThreadedRequest(cluster)
        logging.info("Benchmark starts for {}".format(cluster))
        th_req.send_case_scenarios()
        logging.info("Benchmark finishes for {}".format(cluster))

def get_or_create_output_directory():
    # create an ouput directory if it does not already exist
    out_dir = os.path.join(os.getcwd(), 'output/')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)  
    return out_dir 

def get_or_create_logging_file(name):
    # create a logging file if it does not already exist
    logs_dir = os.path.join(get_or_create_output_directory(), 'logs/')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    file_path = os.path.join(logs_dir, name)
    return file_path

def main():
    ec2_url = None

    # Get the env variable containing the load balancer dns
    ec2_url = os.getenv("EC2_URL", default=None)

    if ec2_url is None:
        logging.error("The EC2_URL env variable is not defined.")
        return
    
    # configure the log file
    log_file_name = get_or_create_logging_file('benchmark.log')
    logging.basicConfig(filename=log_file_name,
                        filemode='w',
                        format='%(asctime)s %(message)s', 
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG, 
                        encoding='utf-8')
    
    # start benchmarking
    logging.info('Benchmarking started')
    benchmark(ec2_url)
    logging.info('Benchmarking finished') 

    print('Downloading Widgets')
    # create an image directory if it does not already exist   
    img_dir = os.path.join(get_or_create_output_directory(), 'images/')    
       
    time.sleep(4*60) 

    # download cloudwatch results for the load balancer as png
    print('Downloading ELB Widgets')
    my_widgets = Widgets(img_dir)
    my_widgets.elb_widgets()   
    
    # download cloudwatch results for the target groups as png
    print('Downloading target group Widgets')
    my_widgets.target_group_widgets("tg1")
    my_widgets.target_group_widgets("tg2")

    print('Downloading instances Widgets')
    my_widgets.instances_widgets("cluster1")
    my_widgets.instances_widgets("cluster2")

if __name__ == '__main__':
    main()