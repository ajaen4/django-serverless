# Django Serverless

## Introduction

This project's main objective is to provide Django developers with an easy way of deploying several Django projects on AWS.

## Tech Stack

Technologies used:

- Pulumi
- AWS

## Architecture

<p align="center">
  <img src="images/django-serverless.png?raw=true" alt="Architecture">
</p>

Components per Django project:

- 1 Application Load Balancer (ALB)
- 1 ECS Service
    - N tasks per service (parametrized)
- 1 RDS Database

## Project's structure

- django_services: Django projects implemented.
  - <django_project_name>:
    - ...
    - [management](https://github.com/ajaen4/django-serverless/tree/main/django_services/django_learning/management): app that must be copied and installed into any new project. Used to be able to use custom admin commands.
    - [entrypoint.sh](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/entrypoint.sh): must be copied into any new project. Used to initialize the server correctly on AWS.
    - [Dockerfile](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/Dockerfile): must be copied into any new project. Used to deploy the server on AWS with all the necessary dependencies.
    - requirements.txt: must be included with the necessary dependencies for each Django project + gunicorn==21.2.0 + boto3==1.34.55.
- pulumi: Infrastructure as Code that deploys the infrastructure needed for each Django project.
  - [Pulumi.main.yaml](https://github.com/ajaen4/django-serverless/blob/main/pulumi/Pulumi.main.yaml): config file to let Pulumi know of the characteristics of each of your projects (cpu, memory, number of workers, DB preferences...)

## Configuration schema

The following explains the [IaC config](https://github.com/ajaen4/django-serverless/blob/main/pulumi/Pulumi.main.yaml) file where you would need to fill in your project's settings:

```bash
config:
  aws:region: eu-west-1
  vpc_name: type = str
  add_nat: type = bool, Optional
  django_services: type = dict, Optional
    <django_project_1>:
      backend:
        django_project: type = str
        cpu: type = int, Optional (default = 256). The hard limit of CPU units to present for the task. Expressed using CPU units.
        memory: type = int, Optional (default = 512). The hard limit of memory (in MiB) to present to the task.
        desired_count: type = int, Optional (default = 1). Number of instances of the task definition to place and keep running.
        workers_per_instance: type = int, Optional (default = 1). Number of Django workers per instance.
        lb_port: type = int, Optional (default = 80). Load Balancer port.
        container_port: type = int, Optional (default = 8000). Container port.
        superuser:
          username: type = str. Superuser user name.
          email: str. Superuser email.
      db:
        engine: type = str. The AWS RDS engine. Options: aurora-mysql or aurora-postgresql
        family: type = str. The AWS RDS family.
        version: type = str. The AWS RDS engine version.
        db_name: type = str. DB name to hold Django ORM and internal tables.
        port: type = int. DB port.
    <django_project_2>:
      ...
```

## Important considerations

Some things to take into account before developing with this repo:

- This repo is not production ready:
  - The service doesn't autoscale horizontally, it needs an Auto Scaling Group in AWS to do so.
  - The web page uses HTTP, so the communication is not encrypted.
- You must add the [management app](https://github.com/ajaen4/django-serverless/tree/main/django_services/django_learning/management) stored in the sample project to every new project. This is to be able to use custom commands internally. It's important that you remember to install the app in your settings.py project's file.
- You must also add the [Dockerfile](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/Dockerfile) and the entrypoint.sh to every new Django project.
- You must copy the code used in [settings.py](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/django_learning/settings.py) to access DB secrets in new projects. This is to access the DB secrets in a secure manner, through AWS Parameter Store.
- When deploying locally the Django server will use the SQLite3 DB and will ignore the db config stated in the IaC config. When deploying with Pulumi the Django server will use the config stated in the IaC Config.

## Requirements

- You must own an AWS account and have an Access Key to be able to authenticate. You need this so every script or deployment is done with the correct credentials. See [here](https://docs.aws.amazon.com/cli/latest/reference/configure/) steps to configure your credentials.

- Versions:
    - Pulumi >=3.0.0,<4.0.0
    - Python = 3.11

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
```
In the case of using Microsoft:

```bash
python3 -m venv .venv
.\env\Scripts\activate
```

And to install all required packages:

```bash
pip install -r requirements.txt
```

## Infrastructure deployment

Navigating to the pulumi directory:

```bash
cd pulumi
pulumi up
```

You will enter a dialog where it will ask you if you want to create a stack. Check the pulumi [docs](https://www.pulumi.com/docs/concepts/stack/) for details.

## After deployment

Once you deploy you will se the following outputs:

- Load Balancer DNS: to be able to connect to your deployed app.
- Passwords parameter name: name of the parameter that holds the passwords for the Django super user and the DB admin.

Example:
<p align="center">
  <img src="images/outputs.png?raw=true" alt="Architecture">
</p>