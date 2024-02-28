import json

import pulumi
from pulumi_aws import ec2, lb, iam, cloudwatch, ecs

from networking import Networking, SubnetType
from .repository import Repository
from .image import Image


class ECSService:
    def __init__(self, networking: Networking):
        self.networking = networking
        self.create_resources()

    def create_resources(self):
        self.create_roles()
        self.create_networking()
        self.create_ecs_service()

    def create_networking(self):
        lb_sg = ec2.SecurityGroup(
            "lb-sg",
            name="lb-sg",
            description="Controls access to the ALB",
            vpc_id=self.networking.get_vpc_id(),
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    from_port=80,
                    to_port=80,
                    protocol="tcp",
                    cidr_blocks=["0.0.0.0/0"],
                ),
                ec2.SecurityGroupIngressArgs(
                    from_port=443,
                    to_port=443,
                    protocol="tcp",
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            egress=[
                ec2.SecurityGroupEgressArgs(
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            tags={
                "Name": "lb-sg",
            },
        )

        self.ecs_sg = ec2.SecurityGroup(
            "ecs-sg",
            name="ecs-sg",
            description="Controls access to the ECS Service",
            vpc_id=self.networking.get_vpc_id(),
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    security_groups=[lb_sg.id],
                ),
            ],
            egress=[
                ec2.SecurityGroupEgressArgs(
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            tags={
                "Name": "ecs-sg",
            },
        )

        django_lb = lb.LoadBalancer(
            "django-lb",
            name="django-lb",
            load_balancer_type="application",
            internal=False,
            security_groups=[lb_sg.id],
            subnets=[*self.networking.get_subnet_ids(SubnetType.PUBLIC)],
        )

        self.django_tg = lb.TargetGroup(
            "django-service-tg",
            name="django-service-tg",
            port=80,
            protocol="HTTP",
            vpc_id=self.networking.get_vpc_id(),
            target_type="ip",
            health_check=lb.TargetGroupHealthCheckArgs(
                path="/ping/",
                port="traffic-port",
                healthy_threshold=5,
                unhealthy_threshold=2,
                timeout=2,
                interval=5,
                matcher="200",
            ),
        )

        lb.Listener(
            "django-lb-listener",
            load_balancer_arn=django_lb.arn,
            port=80,
            default_actions=[
                lb.ListenerDefaultActionArgs(
                    type="forward",
                    target_group_arn=self.django_tg.arn,
                ),
            ],
        )

    def create_roles(self):
        ecs_role_policy_document = json.dumps(
            {
                "Version": "2008-10-17",
                "Statement": [
                    {
                        "Action": "sts:AssumeRole",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Effect": "Allow",
                    }
                ],
            }
        )

        ecs_execution_policy_document = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "ecs:StartTask",
                            "ecs:StopTask",
                            "ecs:DescribeTasks",
                            "ecr:GetAuthorizationToken",
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:BatchGetImage",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                            "elasticfilesystem:ClientMount",
                            "elasticfilesystem:ClientWrite",
                            "elasticfilesystem:ClientRootAccess",
                            "elasticfilesystem:DescribeFileSystems",
                        ],
                        "Resource": "*",
                    }
                ],
            }
        )

        ecs_task_role_policy_document = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "elasticloadbalancing:Describe*",
                            "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                            "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                            "ec2:Describe*",
                            "ec2:AuthorizeSecurityGroupIngress",
                            "elasticloadbalancing:RegisterTargets",
                            "elasticloadbalancing:DeregisterTargets",
                            "elasticfilesystem:ClientMount",
                            "elasticfilesystem:ClientWrite",
                            "elasticfilesystem:ClientRootAccess",
                            "elasticfilesystem:DescribeFileSystems",
                        ],
                        "Resource": "*",
                    }
                ],
            }
        )

        self.ecs_execution_role = iam.Role(
            "ecs-execution-role",
            name="ecs_execution_role",
            assume_role_policy=ecs_role_policy_document,
        )

        iam.RolePolicy(
            "ecs-execution-role-policy",
            name="ecs_execution_role_policy",
            policy=ecs_execution_policy_document,
            role=self.ecs_execution_role.id,
        )

        self.ecs_task_role = iam.Role(
            "ecs-task-role",
            name="ecs_task_role",
            assume_role_policy=ecs_role_policy_document,
        )

        iam.RolePolicy(
            "ecs-task-role-policy",
            name="ecs_task_role_policy",
            policy=ecs_task_role_policy_document,
            role=self.ecs_task_role.id,
        )

    def create_ecs_service(self):
        CONTAINER_NAME = "django-app"

        repository = Repository(f"{CONTAINER_NAME}-repository")
        image = Image(CONTAINER_NAME, repository.get_repository())
        image_uri = image.push_image("0.0.1")

        django_log_group = cloudwatch.LogGroup(
            "django-log-group",
            name=f"/ecs/{CONTAINER_NAME}",
            retention_in_days=30,
        )

        ecs_cluster = ecs.Cluster("django-app-cluster", name="django-app-cluster")

        container_definitions_template = pulumi.Output.all(
            image_uri=image_uri, log_group_name=django_log_group.name
        ).apply(
            lambda args: json.dumps(
                [
                    {
                        "name": CONTAINER_NAME,
                        "image": args["image_uri"],
                        "essential": True,
                        "cpu": 10,
                        "memory": 512,
                        "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
                        "command": [
                            "gunicorn",
                            "-w",
                            "3",
                            "-b",
                            ":8000",
                            "django_learning.wsgi:application",
                        ],
                        "environment": [],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": args["log_group_name"],
                                "awslogs-region": "eu-west-1",
                                "awslogs-stream-prefix": f"{CONTAINER_NAME}-log-stream",
                            },
                        },
                    }
                ]
            )
        )

        ecs_task_definition = ecs.TaskDefinition(
            "django-app-tf",
            family=CONTAINER_NAME,
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            cpu=256,
            memory=512,
            execution_role_arn=self.ecs_execution_role.arn,
            task_role_arn=self.ecs_task_role.arn,
            container_definitions=container_definitions_template,
        )

        ecs.Service(
            "django-app-service",
            name="django-app-service",
            cluster=ecs_cluster.id,
            task_definition=ecs_task_definition.arn,
            launch_type="FARGATE",
            desired_count=1,
            network_configuration=ecs.ServiceNetworkConfigurationArgs(
                subnets=[
                    *self.networking.get_subnet_ids(SubnetType.PUBLIC),
                ],
                security_groups=[
                    self.ecs_sg.id,
                ],
                assign_public_ip=True,
            ),
            load_balancers=[
                ecs.ServiceLoadBalancerArgs(
                    target_group_arn=self.django_tg.arn,
                    container_name=CONTAINER_NAME,
                    container_port=8000,
                )
            ],
        )
