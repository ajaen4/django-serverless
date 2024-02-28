import json

from pulumi_aws import iam

from networking import Networking
from input_schemas import DjangoServiceCfg
from .ecs_service import ECSService


class ECSServices:
    def __init__(self, networking: Networking, django_srvs_cfg: list[DjangoServiceCfg]):
        self.networking = networking
        self.django_srvs_cfg = django_srvs_cfg
        self.roles = dict()
        self.create_common_resources()

    def create_common_resources(self):
        self.create_roles()
        self.create_services()

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

        ecs_execution_role = iam.Role(
            "ecs-execution-role",
            name="ecs_execution_role",
            assume_role_policy=ecs_role_policy_document,
        )

        self.roles["ecs_execution_role"] = ecs_execution_role

        iam.RolePolicy(
            "ecs-execution-role-policy",
            name="ecs_execution_role_policy",
            policy=ecs_execution_policy_document,
            role=ecs_execution_role.id,
        )

        ecs_task_role = iam.Role(
            "ecs-task-role",
            name="ecs_task_role",
            assume_role_policy=ecs_role_policy_document,
        )

        iam.RolePolicy(
            "ecs-task-role-policy",
            name="ecs_task_role_policy",
            policy=ecs_task_role_policy_document,
            role=ecs_task_role.id,
        )

        self.roles["ecs_task_role"] = ecs_task_role

    def create_services(self):
        for django_srv_cfg in self.django_srvs_cfg:
            ECSService(self.networking, django_srv_cfg, self.roles)
