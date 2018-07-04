[![Build Status](https://travis-ci.org/AlexIoannides/py-docker-aws-example-project.svg?branch=master)](https://travis-ci.org/AlexIoannides/py-docker-aws-example-project)

# Automated Testing and Deployment of a Python Micro-service to AWS, using Docker, Boto3 and Travis-CI

The purpose of this project is to demonstrate how to automate the testing and deployment of a simple Flask-based (RESTful) micro-service to a production-like environment on AWS. The deployment pipeline is handled by [Travis-CI](https://travis-ci.org), that has been granted access to this GitHub repository and configured to run upon a pull request or a merge to the master branch. The pipeline is defined in the `.travis.yaml` file and consists of the following steps:

1. define which Python version to use;
2. install the `Pipenv` package using `pip`;
3. use `Pipenv` to install the project dependencies defined in `Pipfile.lock`;
4. run unit tests by executing `pipenv run python -m unittest tests/*.py`; and,
5. if on the `master` branch - e.g. if a pull request has been merged - then start Docker and run the `deploy_to_aws.py` script.

The `deploy_to_aws.py` script defines the deployment process, which performs the following steps without any manual intervention:

1. build the required Docker image;
2. pushe the image to AWS's Elastic Container Registry (ECR); and,
3. trigger a rolling redeployment of the service across an Elastic Container Service (ECS) cluster.

It is reliant on the definition of three environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_REGION`. For security reasons, these are kept out of the `.travis.yml` and are instead defined using the Travis-CI UI.

Although the micro-service used in this example - as defined in `microservice/api.py` module - only returns a simple message upon a simple `GET` request, it could just as easily be a Machine Learning (ML) model-scoring service that receives the values of feature variables and returns a prediction - the overall pattern is the same.

## Initial Configuration of AWS Infrastructure

Currently, the initial setup of the required AWS infrastructure is entirely manual (although this could also be scripted in the future). What's required, is an ECS cluster that is capable hosting multiple groups of Docker containers (or 'tasks' - i.e. web applications or in our case just a single micro-service), that sit behind a load balances that accepts incoming traffic and routes it to different containers in the cluster. Collectively,this constitutes a 'service' that is highly available. At a high-level, the steps required to setup this infrastructure using the AWS management console, are as follows (assuming the existence of a repository in ECR, containing our docker image):

1. create a new ECS cluster, in new VPC, using instance that are ~ `t2.medium`;
    - when configuring the security group (firewall) for the cluster, consider allowing a rule for single IP to assist debugging (e.g. YOUR_LOCAL_IP_ADDRESS/32);
2. create a new application load balancer for new VPC;
    - then create a custom security group for the load balancer (from the EC2 console), that allows anything from the outside world to pass;
3. modify ECS cluster's security group to allow the load balancer access, by explicitly referencing the security group for the load balancer, that we have just created;
4. create a new target group for the new VPC (from within the EC2 console under the 'Load Balancers' section), which we will eventually point the load balancer to;
    - there is no need to add the instances from the ECS cluster in this step, as this will he handled automatically when creating the service;
    - modify the health check path to `/microservice`, otherwise it won't get 200s and and will try to re-register hosts;
5. create a new task in ECS;
    - for the sake of simplicity, choose `daemon` mode - i.e. assume there is only one container per-task;
    - when adding the container for the task, be sure to reference the Docker image uploaded to ECR;
6. create a new service for our ECS cluster;
    - referencing the task, load balancer and target group that we have created in the steps above.

## Project Dependencies

We use [pipenv](https://docs.pipenv.org) for managing project dependencies and Python environments (i.e. virtual environments). All of the direct packages dependencies required to run the code (e.g. docker and boto3), as well as all the packages used during development (e.g. IPython for interactive console sessions), are described in the `Pipfile`. Their precise downstream dependencies are described in `Pipfile.lock`.

### Installing Pipenv

To get started with Pipenv, first of all download it - assuming that there is a global version of Python available on your system and on the PATH, then this can be achieved by running the following command,

```bash
pip3 install pipenv
```

Pipenv is also available to install from many non-Python package managers. For example, on OS X it can be installed using the [Homebrew](https://brew.sh) package manager, with the following terminal command,

```bash
brew install pipenv
```

For more information, including advanced configuration options, see the [official pipenv documentation](https://docs.pipenv.org).

### Installing this Projects' Dependencies

Make sure that you're in the project's root directory (the same one in which `Pipfile` resides), and then run,

```bash
pipenv install --dev
```

This will install all of the direct project dependencies as well as the development dependencies (the latter a consequence of the `--dev` flag).

### Running Python and IPython from the Project's Virtual Environment

In order to continue development in a Python environment that precisely mimics the one the project was initially developed with, use Pipenv from the command line as follows,

```bash
pipenv run python3
```

The `python3` command could just as well be `ipython3` or the Jupyter notebook server, for example,

```bash
pipenv run jupyter notebook
```

This will fire-up a Jupyter notebook server where the default Python 3 kernel includes all of the direct and development project dependencies. This is how we advise that the notebooks within this project are used.

## Running Unit Tests

All test have been written using the [unittest](https://docs.python.org/3/library/unittest.html) package from the Python standard library. Tests are kept in the `tests` folder and can be run from the command line by - e.g. by evoking,

```bash
pipenv run python -m unittest tests/test_*.py
```

## Starting the Micro-service Locally

This can be started via the command line, from the root directory using,

```bash
pipenv run python -m microservice.api
```

Which will start the server at `http://localhost:5000/microservice`.