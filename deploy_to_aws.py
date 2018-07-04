"""
deploy_to_aws.py
~~~~~~~~~~~~~~~~

A simple script that demonstrates how the docker and AWS Python clients
can be used to automate the process of: building a Docker image, as
defined by the Dockerfile in the project's root directory; pushing the
image to AWS's Elastic Container Registry (ECR); and, then forcing a
redeployment of a AWS Elastic Container Service (ECS) that uses the
image to host the service. 

For now, it is assumed that the AWS infrastructure is already in
existence and that Docker is running on the host machine.
"""

import base64
import json
import os

import boto3
import docker

ECS_CLUSTER = 'py-docker-aws-example-project-cluster'
ECS_SERVICE = 'py-docker-aws-example-project-service'

LOCAL_REPOSITORY = 'py-docker-aws-example-project:latest'


def main():
    """Build Docker image, push to AWS and update ECS service.
    
    :rtype: None
    """

    # get AWS credentials
    aws_credentials = read_aws_credentials()
    access_key_id = aws_credentials['access_key_id']
    secret_access_key = aws_credentials['secret_access_key']
    aws_region = aws_credentials['region']

    # build Docker image
    docker_client = docker.from_env()
    image, build_log = docker_client.images.build(
        path='.', tag=LOCAL_REPOSITORY, rm=True)

    # get AWS ECR login token
    ecr_client = boto3.client(
        'ecr', aws_access_key_id=access_key_id, 
        aws_secret_access_key=secret_access_key, region_name=aws_region)

    ecr_credentials = (
        ecr_client
        .get_authorization_token()
        ['authorizationData'][0])

    ecr_username = 'AWS'

    ecr_password = (
        base64.b64decode(ecr_credentials['authorizationToken'])
        .replace(b'AWS:', b'')
        .decode('utf-8'))

    ecr_url = ecr_credentials['proxyEndpoint']

    # get Docker to login/authenticate with ECR
    docker_client.login(
        username=ecr_username, password=ecr_password, registry=ecr_url)

    # tag image for AWS ECR
    ecr_repo_name = '{}/{}'.format(
        ecr_url.replace('https://', ''), LOCAL_REPOSITORY)

    image.tag(ecr_repo_name, tag='latest')

    # push image to AWS ECR
    push_log = docker_client.images.push(ecr_repo_name, tag='latest')

    # force new deployment of ECS service
    ecs_client = boto3.client(
        'ecs', aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key, region_name=aws_region)

    ecs_client.update_service(
        cluster=ECS_CLUSTER, service=ECS_SERVICE, forceNewDeployment=True)

    return None


def read_aws_credentials(filename='.aws_credentials.json'):
    """Read AWS credentials from file.
    
    :param filename: Credentials filename, defaults to '.aws_credentials.json'
    :param filename: str, optional
    :return: Dictionary of AWS credentials.
    :rtype: Dict[str, str]
    """

    try:
        with open(filename) as json_data:
            credentials = json.load(json_data)

        for variable in ('access_key_id', 'secret_access_key', 'region'):
            if variable not in credentials.keys():
                msg = '"{}" cannot be found in {}'.format(variable, filename)
                raise KeyError(msg)
                                
    except FileNotFoundError:
        try:
            credentials = {
                'access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                'secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                'region': os.environ['AWS_REGION']
            }
        except KeyError:
            msg = 'no AWS credentials found in file or environment variables'
            raise RuntimeError(msg)

    return credentials


if __name__ == '__main__':
    main()