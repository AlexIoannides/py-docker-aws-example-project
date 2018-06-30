"""
deploy_to_aws.py
~~~~~~~~~~~~~~~~

"""

import boto3

AWS_ACCESS_KEY_ID = 'AKIAI5V3AYAPFMLCXSHQ'
AWS_SECRET_ACCESS_KEY = 'hqzqA4Xhm7e3yh809OLTwY//E/o1pgp5jq3fH6Bt'
AWS_REGION_NAME = 'eu-west-2'

# ECR example
ecr = boto3.client(
    'ecr',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION_NAME,
)

ecr_reg_token = (
    ecr
    .get_authorization_token()
    ['authorizationData'][0]['authorizationToken'])

print(ecr_reg_token)

# docker login
# TODO

# build image
# TODO

# push image
# TODO

# [optional] create cluster in new VPC with >= t2.medium
# -> in security group (firewall) setup allow rule for single IP to assist debugging (e.g. 82.16.104.175/32)
# TODO

# [optional] create application load balancer for new VPC 
# -> create custom security group for the ELB that allows anything from the outside world
# TODO

# [optional] modify cluster security group to allow ELB access (reference ELB's security group)
# TODO

# [optional] create target group for new VPC (no need to add the instances in this step)
# -> modify the health check path to /microservice otherwise it won't get 200s and and re-register hosts
# TODO

# create/update task
# TODO

# create/update service and choose application load balancing 
# TODO
