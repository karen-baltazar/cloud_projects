import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')

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
    
def create_key_pair(name):
    # if key_pair does not exist, create one
    try:
        ec2_client.describe_key_pairs(KeyNames=[name])
    except ClientError as e:
        ec2.create_key_pair(KeyName=name)
    return ec2_client.describe_key_pairs(KeyNames=[name], IncludePublicKey=True)['KeyPairs'][0]['PublicKey']

def create_security_group(name, desc, vpc_id):
    # if security group does not exist, create one
    try:
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]
    except ClientError as e:
        ec2.create_security_group(GroupName=name, Description = desc, VpcId=vpc_id)
    
        sg = ec2_client.describe_security_groups(GroupNames=[name])['SecurityGroups'][0]

        # add rules for security
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
    
def create_cluster(count, instance_type, key_name, zone, subnet, security_group):        
    # create the cluster
    cluster = ec2.create_instances(
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
        
    return cluster
    
    
def main():
    KEY_NAME = 'ms_kp_pem'
    SECURITY_GROUP_NAME = 'securityGroup2'
    ZONE_NAME = 'us-east-1a'

    vpc_id = ec2_client.describe_vpcs()['Vpcs'][0]['VpcId']
    security_group = create_security_group(name=SECURITY_GROUP_NAME, desc='TP2 security group', vpc_id=vpc_id)
    key_obj=create_key_pair(KEY_NAME)
    zone_subnet_id = get_subnet_id(ZONE_NAME)        
        
    cluster = create_cluster(1, 'm4.large', KEY_NAME, ZONE_NAME, zone_subnet_id, security_group)
    # start the cluster single node
    instance_ids =  [instance.id for instance in cluster]
    ec2_client.start_instances(InstanceIds = instance_ids)
    # wait for all instances to be running before proceeding        
    waiter = ec2_client.get_waiter('instance_running')
    waiter.wait(InstanceIds = instance_ids)

    # allocate Elastic IP
    allocation_response = ec2_client.allocate_address(
        Domain='vpc',
    )

    # associate Elastic IP to the instance
    ec2_client.associate_address(
        AllocationId=allocation_response['AllocationId'],
        InstanceId=instance_ids[0],
    )

    # reload the instance attributes
    cluster[0].reload()   

    # take the name part
    key_pair_name = key_obj.split()[2]

    # output the {key name}:{dns name}
    print(f'{key_pair_name}.pem:{cluster[0].public_dns_name}')

if __name__ == "__main__":
    main()