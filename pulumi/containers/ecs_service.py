import json

import pulumi
from pulumi_aws import ec2, lb, cloudwatch, ecs, iam

from networking import Networking
from input_schemas import SubnetType, DjangoServiceCfg
from .repository import Repository
from .image import Image


class ECSService:
    def __init__(
        self,
        networking: Networking,
        django_srv_cfg: DjangoServiceCfg,
        roles: dict[str, iam.Role],
    ):
        self.networking = networking
        self.django_srv_cfg = django_srv_cfg
        self.roles = roles
        self.create_resources()

    def create_resources(self):
        self.create_networking()
        self.create_ecs_service()

    def create_networking(self):
        service_name = self.django_srv_cfg.service_name.replace("_", "-")

        lb_sg = ec2.SecurityGroup(
            f"{service_name}-lb-sg",
            name=f"{service_name}-lb-sg",
            description="Controls access to the ALB",
            vpc_id=self.networking.get_vpc_id(),
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    from_port=self.django_srv_cfg.lb_port,
                    to_port=self.django_srv_cfg.lb_port,
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
                "Name": f"{service_name}-lb-sg",
            },
        )

        self.ecs_sg = ec2.SecurityGroup(
            f"{service_name}-sg",
            name=f"{service_name}-ecs-sg",
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
            f"{service_name}-lb",
            name=f"{service_name}-lb",
            load_balancer_type="application",
            internal=False,
            security_groups=[lb_sg.id],
            subnets=[*self.networking.get_subnet_ids(SubnetType.PUBLIC)],
        )

        self.django_tg = lb.TargetGroup(
            f"{service_name}-service-tg",
            name=f"{service_name}-service-tg",
            port=self.django_srv_cfg.lb_port,
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
            f"{service_name}-lb-listener",
            load_balancer_arn=django_lb.arn,
            port=self.django_srv_cfg.lb_port,
            default_actions=[
                lb.ListenerDefaultActionArgs(
                    type="forward",
                    target_group_arn=self.django_tg.arn,
                ),
            ],
        )

    def create_ecs_service(self):
        service_name = self.django_srv_cfg.service_name

        repository = Repository(f"{service_name}-repository")
        image = Image(
            service_name,
            self.django_srv_cfg.django_project,
            repository.get_repository(),
        )
        image_uri = image.push_image("0.0.1")

        django_log_group = cloudwatch.LogGroup(
            f"{service_name}-log-group",
            name=f"/ecs/{service_name}",
            retention_in_days=30,
        )

        ecs_cluster = ecs.Cluster(
            f"{service_name}-cluster", name=f"{service_name}-cluster"
        )

        container_definitions_template = pulumi.Output.all(
            image_uri=image_uri, log_group_name=django_log_group.name
        ).apply(
            lambda args: json.dumps(
                [
                    {
                        "name": service_name,
                        "image": args["image_uri"],
                        "essential": True,
                        "cpu": 10,
                        "memory": 512,
                        "portMappings": [
                            {
                                "containerPort": self.django_srv_cfg.container_port,
                                "protocol": "tcp",
                            }
                        ],
                        "command": [
                            "gunicorn",
                            "-w",
                            "3",
                            "-b",
                            f":{self.django_srv_cfg.container_port}",
                            "django_learning.wsgi:application",
                        ],
                        "environment": [],
                        "logConfiguration": {
                            "logDriver": "awslogs",
                            "options": {
                                "awslogs-group": args["log_group_name"],
                                "awslogs-region": "eu-west-1",
                                "awslogs-stream-prefix": f"{service_name}-log-stream",
                            },
                        },
                    }
                ]
            )
        )

        ecs_task_definition = ecs.TaskDefinition(
            f"{service_name}-tf",
            family=service_name,
            network_mode="awsvpc",
            requires_compatibilities=["FARGATE"],
            cpu=self.django_srv_cfg.cpu,
            memory=self.django_srv_cfg.memory,
            execution_role_arn=self.roles["ecs_execution_role"].arn,
            task_role_arn=self.roles["ecs_task_role"].arn,
            container_definitions=container_definitions_template,
        )

        ecs.Service(
            f"{service_name}-service",
            name=f"{service_name}-service",
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
                    container_name=service_name,
                    container_port=self.django_srv_cfg.container_port,
                )
            ],
        )
