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

def create_security_group(name, desc, vpc_id):
    # If security group does not exist, create one
    try:
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]
    except ClientError as e:
        ec2.create_security_group(GroupName=name, Description = desc, VpcId=vpc_id)
    
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]

        # Add rules for security
        ec2_client.authorize_security_group_ingress(
            GroupId = sg['GroupId'],
            IpPermissions = [
            {
                'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            },
            {
                'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
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

def create_instance(count, instance_type, key_name, zone, subnet, security_group):        
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
        
    return instance

def main():
    # Create key pair
    key_name = 'ms_kp_pem'
    key_obj = create_key_pair(key_name)

    # Create security group
    security_group_name = 'securityGroup'
    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']
    security_group = create_security_group(name = security_group_name, desc='TP3 - Security Group', vpc_id=vpc_id)

    # Create EC2 instance
    zone_name = 'us-east-1a'
    zone_subnet_id = get_subnet_id(zone_name)        
    instance = create_instance(1, 't2.micro', key_name, zone_name, zone_subnet_id, security_group)

    # Wait for the instance to enter the running state
    instance[0].wait_until_running()

    # Reload the instance attributes
    instance[0].load()

    # Extract the key name part
    key_pair_name = key_obj.split()[2]

    # Output {key name}:{DNS name}
    print(f'{key_pair_name}.pem:{instance[0].public_dns_name}')

if __name__ == "__main__":
    main()