import boto3
from botocore.exceptions import ClientError

# Create an EC2 client
ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

def create_key_pair(name):
    # If key pair does not exist, create one
    try:
        ec2_client.describe_key_pairs(KeyNames=[name])
    except ClientError as e:
        ec2.create_key_pair(KeyName=name)
    return ec2_client.describe_key_pairs(KeyNames=[name], IncludePublicKey=True)['KeyPairs'][0]['PublicKey']

def create_security_group_with_ports(name, desc, vpc_id, common_ports, additional_ports):
    try:
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]
    except ClientError as e:
        ec2.create_security_group(GroupName=name, Description=desc, VpcId=vpc_id)

        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]

        # Add common ports
        for port in common_ports:
            ec2_client.authorize_security_group_ingress(
                GroupId=sg['GroupId'],
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                ])

        # Add additional ports
        for port in additional_ports:
            ec2_client.authorize_security_group_ingress(
                GroupId=sg['GroupId'],
                IpPermissions=[
                    {
                        'IpProtocol': 'tcp',
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    },
                ])

    return sg

def get_subnet_id(zone):
    # Get the subnet_id based on the availability-zone
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

def create_instances(count, instance_type, key_name, zone, subnet, security_group):        
    # Define parameters for the instance
    instance = ec2.create_instances(
        ImageId = 'ami-0fc5d935ebf8bc3bc',
        MinCount = count,
        MaxCount = count,
        InstanceType = instance_type,
        KeyName = key_name,
        Placement = {
            'AvailabilityZone': zone
        },     
        SubnetId = subnet,
        SecurityGroupIds = [ security_group['GroupId'] ]           
    )
        
    return instances

def main():
    # Create key pair
    key_name = 'ms_kp_pem'
    key_obj = create_key_pair(key_name)
    key_pair_name = key_obj.split()[2]
    print(f'{key_pair_name}.pem')

    # List to store private IP addresses
    private_ip_addresses = []

    # Create security groups for database, trusted host, gatekeeper, and proxy
    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']
    common_ports = [80, 22, 443]

    # Define security group information
    security_groups_to_create = [
        {'name': 'database_sg', 'desc': 'Security Group for Database Instances', 'additional_ports': []},
        {'name': 'proxy_sg', 'desc': 'Security Group for Proxy', 'additional_ports': [60000]},
        {'name': 'gatekeeper_sg', 'desc': 'Security Group for Gatekeeper', 'additional_ports': [50000]},
        {'name': 'trusted_host_sg', 'desc': 'Security Group for Trusted Host', 'additional_ports': [50000, 60000]},
    ]

    # Create security groups
    for sg_info in security_groups_to_create:
        security_group = create_security_group_with_ports(sg_info['name'], sg_info['desc'], vpc_id, common_ports, sg_info['additional_ports'])

    # Create database instances [stand-alone/cluster]
    zone_name = 'us-east-1a'
    zone_subnet_id = get_subnet_id(zone_name)
    cluster = create_instances(5, 't2.micro', key_name, zone_name, zone_subnet_id, security_group[0])

    # Wait for the instances to enter the running state
    for instance in cluster:
        instance.wait_until_running()

        # Reload the instance attributes
        instance.load()

        # Get and store the private IP address
        private_ip_addresses.append(instance.private_ip_address)

        # Output {DNS name}
        print(f'{instance.public_dns_name}')

    # Skip the first IP if there is at least one instance in the cluster
    if private_ip_addresses:
        private_ip_addresses = private_ip_addresses[1:]

    # Create trusted host, gatekeeper, and proxy instances
    instances_to_create = [
        {'name': 'Proxy', 'type': 't2.large', 'sg': security_group[1]},
        {'name': 'Gatekeeper', 'type': 't2.large', 'sg': security_group[2]},
        {'name': 'Trusted Host', 'type': 't2.large', 'sg': security_group[3]},
    ]

    for instance_info in instances_to_create:
        instance = create_instances(1, instance_info['type'], key_name, zone_name, zone_subnet_id, instance_info['sg'])[0]
        instance.wait_until_running()
        instance.load()
        private_ip_addresses.append(instance.private_ip_address)
        print(f'{instance.public_dns_name}')

    # Save private IP addresses to a text file
    with open('private_ips.txt', 'w') as file:
        for ip in private_ip_addresses:
            file.write(f'{ip}\n')

if __name__ == "__main__":
    main()