import boto3
import json
import os

class Widgets:
    def __init__(self, workdir):
        self.directory = workdir
        self.cloudwatch = boto3.client('cloudwatch')
        self.elb = boto3.client('elbv2')
        self.ec2_resource = boto3.resource('ec2')
        self.elb_id = None

    def elb_widgets(self):
        response = self.elb.describe_load_balancers()['LoadBalancers'][0]['LoadBalancerArn']
        # get the load balancer Arn

        lb_array = response.split(':')
        lb_string = lb_array[-1]
        lb_array2 = lb_string.split('/')
        self.elb_id = lb_array2[1] + '/' + lb_array2[2] + '/' + lb_array2[3]  

        # create a load balancer directory for the png files if it does not already exist   
        dir = os.path.join(self.directory, 'load-balancer')
        if not os.path.exists(dir):
                os.makedirs(dir)     
        
        # define the load balancer metrics
        dict = {
                'ActiveConnectionCount' : 'Sum', 
                'ConsumedLCUs' : 'Sum',
                'NewConnectionCount' : 'Sum',
                'ProcessedBytes' : 'Sum' ,
                'RequestCount' : 'Sum' ,
                'RuleEvaluations' : 'Sum' ,
                'HTTPCode_Target_2XX_Count' : 'Sum',
                'TargetResponseTime' : 'Average'
                }
        
        for k, v in dict.items():
            metrics_array = ['AWS/ApplicationELB', k, 'LoadBalancer', self.elb_id, { 'label': self.elb_id, 'yAxis' : 'left' }]
            metric_widget = {
                'metrics': [metrics_array],
                'period': 60,
                'region': 'us-east-1',
                'view': 'timeSeries',
                'title': f'Graph of {k}',
                'liveData': False,
                'start': '-PT30M',
                'end': 'P0D',
                'timezone': '-0400',
                'stat': v 
            }

            # get the metrics and create the png file
            json_str = json.dumps(metric_widget, indent=4)
            response = self.cloudwatch.get_metric_widget_image(
                MetricWidget = json_str,
                OutputFormat = 'png'
            )

            file_path = os.path.join(dir, f'{k}.png')

            with open(file_path, "wb") as file:
                file.write(response['MetricWidgetImage'])

    def target_group_widgets(self, target_group_name):
        response = self.elb.describe_target_groups(Names=[target_group_name])
        if 'TargetGroups' in response and len(response['TargetGroups']) > 0:
            target_group_id = response['TargetGroups'][0]['TargetGroupArn'].split(':')[-1]


        # create a target group directory for the png files if it does not already exist   
        dir = os.path.join(self.directory, f'target-group-{target_group_name}')
        if not os.path.exists(dir):
                os.makedirs(dir)     
        
        # define the target group metrics
        dict = {
                'HealthyHostCount' : 'Average' ,
                'HTTPCode_Target_2XX_Count' : 'Sum',
                'RequestCountPerTarget' : 'Sum' ,
                'TargetResponseTime' : 'Average'
                }
        
        for k, v in dict.items():
            metrics_array = ['AWS/ApplicationELB', k, 'TargetGroup', target_group_id, 'LoadBalancer', self.elb_id, { 'label': target_group_id, 'yAxis' : 'left' }]
            metric_widget = {
                'metrics': [metrics_array],
                'period': 60,
                'region': 'us-east-1',
                'view': 'timeSeries',
                'title': f'Graph of {k}',
                'liveData': False,
                'start': '-PT30M',
                'end': 'P0D',
                'timezone': '-0400',
                'stat': v 
            }

            # get the metrics and create the png file
            json_str = json.dumps(metric_widget, indent=4)
            response = self.cloudwatch.get_metric_widget_image(
                MetricWidget = json_str,
                OutputFormat='png'
            )

            file_path = os.path.join(dir, f'{k}.png')

            with open(file_path, "wb") as file:
                file.write(response['MetricWidgetImage'])

    
    def instances_widgets(self, cluster_name):
        custom_filter = [
            {'Name':'tag:ClusterName', 'Values': [cluster_name] }, 
            {'Name': 'instance-state-name', 'Values': ['running'] } 
        ] 

        instances = self.ec2_resource.instances.filter(Filters=custom_filter)
        instance_ids = [ instance.id for instance in instances ]

        dir = os.path.join(self.directory, cluster_name)
        if not os.path.exists(dir):
                os.makedirs(dir)    

        metrics = [ 'CPUUtilization', 'DiskReadOps', 'DiskWriteOps', 'DiskReadBytes', 'DiskWriteBytes', 'MetadataNoToken',
                   'NetworkIn', 'NetworkOut', 'NetworkPacketsIn', 'NetworkPacketsOut', 'CPUCreditUsage', 'CPUCreditBalance',
                   'StatusCheckFailed', 'StatusCheckFailed_Instance', 'StatusCheckFailed_System']           
        
        for metric in metrics:
            metrics_array = []

            for id in instance_ids:
                metrics_array.append(['AWS/EC2', metric, 'InstanceId', id, { 'label': id, 'yAxis' : 'left' }])

            metric_widget = {
                'metrics': metrics_array,
                'period': 60,
                'region': 'us-east-1',
                'view': 'timeSeries',
                'title': f'Graph of {metric}',
                'liveData': False,
                'start': '-PT30M',
                'end': 'P0D',
                'timezone': '-0400'             
            }

            json_str = json.dumps(metric_widget, indent=4)
            response = self.cloudwatch.get_metric_widget_image(
                MetricWidget = json_str,
                OutputFormat='png'
            )

            file_path = os.path.join(dir, f'{metric}.png')

            with open(file_path, "wb") as file:
                file.write(response['MetricWidgetImage'])