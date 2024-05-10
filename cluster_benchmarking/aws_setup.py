import os
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

elb = boto3.client('elbv2')

def get_subnet_id(zone):
    # get the subnet_id based on the availability-zone
    subnetId = ec2_client.describe_subnets(
        Filters = [
            {
                'Name': 'availability-zone',
                'Values': [
                    zone
                ]
            },
        ])['Subnets'][0]['SubnetId']
    return subnetId

def create_a_key_pair(name):
    # if key_pair does not exist, create one
    try:
        ec2_client.describe_key_pairs(KeyNames=[name])
    except ClientError as e:
        ec2.create_key_pair(KeyName=name)
    return ec2_client.describe_key_pairs(KeyNames=[name], IncludePublicKey=True)['KeyPairs'][0]['PublicKey']

def create_a_security_group(name, desc, vpc_id):
    # if security group does not exist, create one
    try:
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]
    except ClientError as e:
        ec2.create_security_group(GroupName=name, Description = desc, VpcId=vpc_id)
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]

        # add two rules for security
        ec2_client.authorize_security_group_ingress(
                GroupId = sg['GroupId'],
                IpPermissions = [
                    {'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                    {'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }
                ]) 
    return sg

def create_cluster(count, instance_type, key_name, zone, subnet, sg, cluster_ordinal_nb: int):
    # add the bash script to deploy the flask app in each of the instances
    if os.path.exists('deploy_flask_app.sh'):
        with open('deploy_flask_app.sh', 'r') as file:
            user_script = file.read() % cluster_ordinal_nb
    
    # create the cluster of instances
    cluster = ec2.create_instances(
        ImageId = "ami-053b0d53c279acc90",
        MinCount = count,
        MaxCount = count,
        InstanceType = instance_type,
        KeyName = key_name,
        Placement = {
            'AvailabilityZone': zone
        },     
        SubnetId = subnet,
        SecurityGroupIds = [ sg['GroupId'] ],
        UserData = user_script,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{
                'Key': 'ClusterName',
                'Value': f'cluster{cluster_ordinal_nb}'
            }],
        }],
        Monitoring={
            'Enabled': True
        }
    )
    
    return cluster

def create_a_target_group(tg_name, vpc_id, path):
    try:
        # create a target group
        tg = elb.create_target_group(
            Name = tg_name,
            Protocol = 'HTTP',
            Port = 80,
            VpcId = vpc_id,
            HealthCheckProtocol = 'HTTP',
            HealthCheckPath = path,
            HealthCheckPort='80'
        )
    except elb.exceptions.DuplicateTargetGroupNameException:
        response = elb.parent.elbv2.describe_target_groups( Names=[ tg_name ] )
        elb.delete_target_group(
            TargetGroupArn = response['TargetGroups'][0]['TargetGroupArn']
        )
        tg = elb.create_target_group(
            Name = tg_name,
            Protocol = 'HTTP',
            Port = 80,
            VpcId = vpc_id,
            HealthCheckProtocol = 'HTTP',
            HealthCheckPath = path,
            HealthCheckPort='80'
        )

    return tg

def create_load_balancer(lb_name, subnets, sg):
    # create a load balancer
    load_balancer = elb.create_load_balancer(
        Name = lb_name,
        Subnets = subnets,
        SecurityGroups = [ sg['GroupId'] ],
        Scheme = 'internet-facing',
        Type = 'application',
        IpAddressType = 'ipv4'
    )

    return load_balancer

def create_a_listener(lb):
    # create a listener fore the load balancer
    listener = elb.create_listener(
        LoadBalancerArn = lb['LoadBalancers'][0]['LoadBalancerArn'],
        Protocol = 'HTTP',
        Port = 80,
        DefaultActions = [
            {
                'Type': 'fixed-response',
                'FixedResponseConfig': {
                    'StatusCode': '400',
                    'ContentType': 'text/plain',
                    'MessageBody': 'Bad Request'
                }
            }
        ]
    )
    return listener

def create_a_rule(listener, target_group_arn, path, priority):
    # create a rule for the target group
    rule = elb.create_rule(
        ListenerArn = listener['Listeners'][0]['ListenerArn'],
        Conditions = [
            {
                'Field': 'path-pattern',
                'Values': [path]
            }
        ],
        Priority = priority,
        Actions = [
            {
                'Type': 'forward',
                'TargetGroupArn': target_group_arn
            }
        ]
    )
    return rule

def register_instances(target_group_arn, instances, target_count):
    # register the instances to the appropriate target group
    elb.register_targets(
        TargetGroupArn = target_group_arn,
        Targets = [
            {'Id' : instances[i].id, 'Port': 80} for i in range(target_count)
        ]
    )

def main():
    # Paramter values
    key_name = 'key1'
    security_group_name = 'securityGroup1'
    zone1 = 'us-east-1a'
    zone2 = 'us-east-1b'
    tg1_name = 'tg1'
    tg2_name = 'tg2'
    lb_name = 'load-balancer-1'
    path1 = '/cluster1'
    path2 = '/cluster2'

    # get vpc id
    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']

    # get subnet_id based on both availability zones
    subnet_id_for_zone1 = get_subnet_id(zone1)
    subnet_id_for_zone2 = get_subnet_id(zone2)

    # create a key pair and store public key obtained
    public_key = create_a_key_pair(key_name)

    # create a security group
    sg = create_a_security_group(name=security_group_name, desc='A security group', vpc_id=vpc_id)

    # create the two clusters of instances
    cluster1 = create_cluster(5, 't2.large', key_name, zone1, subnet_id_for_zone1, sg, 1)
    cluster2 = create_cluster(4, 'm4.large', key_name, zone2, subnet_id_for_zone2, sg, 2) 

    # create the target groups for each cluster
    tg1 = create_a_target_group(tg1_name, vpc_id, path1)
    tg2 = create_a_target_group(tg2_name, vpc_id, path2)
    
    # create a load balancer
    lb = create_load_balancer(lb_name, [subnet_id_for_zone1, subnet_id_for_zone2], sg)

    # Get the dns name
    dns_name = lb['LoadBalancers'][0]['DNSName']
    ec2_url = f"http://{dns_name}"

    # create a listener for the load balancer
    listener = create_a_listener(lb)

    # create a rule for each target group
    rule1 = create_a_rule(listener, tg1['TargetGroups'][0]['TargetGroupArn'], path1, 1)
    rule2 = create_a_rule(listener, tg2['TargetGroups'][0]['TargetGroupArn'], path2, 2)

    # start the instances created in cluster 1
    instances_id_cluster1 =  [instance.id for instance in cluster1]
    ec2_client.start_instances(InstanceIds = instances_id_cluster1)   

    # start the instances created in cluster 2
    instances_id_cluster2 =  [instance.id for instance in cluster2]
    ec2_client.start_instances(InstanceIds = instances_id_cluster2)

    # wait for all instances to be running before proceeding
    instanceIds = [*instances_id_cluster1, *instances_id_cluster2]
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instanceIds)

    # register the instances to the appropriate target group
    register_instances(tg1['TargetGroups'][0]['TargetGroupArn'], cluster1, 5)
    register_instances(tg2['TargetGroups'][0]['TargetGroupArn'], cluster2, 4)

    # output the dns name
    print(ec2_url)

if __name__ == "__main__":
    main()