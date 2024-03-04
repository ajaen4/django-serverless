# Django Serverless

## Introduction

This project's main objective is to provide Django developers an easy way of deploying several Django project on AWS.

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
  <django_project_name>:
    - ...
    - [management](https://github.com/ajaen4/django-serverless/tree/main/django_services/django_learning/management): app that must be copied and installed into any new project. Used to be able to use custom admin commands.
    - [entrypoint.sh](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/entrypoint.sh): must be copied into any new project. Used to initialize correctly the server on AWS.
    - [Dockerfile](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/Dockerfile): must be copied into any new project. Used to deploy the server on AWS with all the necessary dependencies.
    - requirements.txt: must be included with the necessary dependencies for each Django project + gunicorn==21.2.0.
- pulumi: Infrastructure as Code that deploys the infrastructure needed for each Django project.
  - Pulumi.main.yaml: config file to let Pulumi know the characteristics of each of your projects (cpu, memory, number of workers, db preferences...)

## Configuration schema

```bash
config:
  aws:region: eu-west-1
  vpc_name: type = str
  add_nat: type = bool, Optional
  django_services: type = dict, Optional
    django_learning:
      backend:
        django_project: type = str
        cpu: type = int, Optional (default = 256). The hard limit of CPU units to present for the task. Expressed using CPU units.
        memory: type = int, Optional (default = 512). The hard limit of memory (in MiB) to present to the task.
        desired_count: type = int, Optional (default = 1). Number of instances of the task definition to place and keep running.
        lb_port: 80 type = int, Optional (default = 80). Load Balancer port.
        container_port: 8000 type = int, Optional (default = 8000). Container port.
        super_user:
          username: type = str. Superuser user name.
          email: str. Superuser email.
      db:
        engine: type = str. The AWS RDS engine. Options: aurora-mysql or aurora-postgresql
        family: type = str. The AWS RDS family.
        version: type = str. The AWS RDS engine version.
        db_name: type = str. DB name to hold Django ORM and internal tables.
        port: type = int. DB port.
```

## Important considerations

Some things to take into account before developing with this repo:

- This repo is not production ready:
  - Passwords for the Django superuser and the DB user are generated randomnly but passed as commands and env variable context in plain text.
  - The service doesn't autoscale horizontally, needs an Auto Scaling Group in AWS to do so.
- You must add the [management app](https://github.com/ajaen4/django-serverless/tree/main/django_services/django_learning/management) stored in the sample project in every new project. This is to be able to use custom commands internally. It's important that you remember to install the app in your settings.py project's file.
- You must also add the [Dockerfile](https://github.com/ajaen4/django-serverless/blob/main/django_services/django_learning/Dockerfile) and the entrypoint.sh to every new Django project.
- When deploying locally the Django server will use the sqlite3 db and will ignore the db config stated in the IaC config. When deploying with Pulumi the Django server will use the config stated in the IaC Config.



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

You will enter a dialog where it will ask you if you want to create a stack. Check the pulumi docs for details.
