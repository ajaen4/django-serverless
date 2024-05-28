from pulumi_aws import ec2, rds
import pulumi_random as random
import pulumi

from input_schemas import DjangoServiceCfg
from networking import Networking
from input_schemas import SubnetType


class RDS:
    def __init__(
        self,
        networking: Networking,
        backend_sg: ec2.SecurityGroup,
        django_srv_cfg: DjangoServiceCfg,
    ) -> None:
        self.service_name = django_srv_cfg.service_name
        self.db_cfg = django_srv_cfg.db_cfg
        self.networking = networking
        self.create_resources(backend_sg)

    def create_resources(self, backend_sg: ec2.SecurityGroup) -> None:
        SERVICE_NAME = self.service_name.replace("_", "-")

        db_sg = ec2.SecurityGroup(
            f"{SERVICE_NAME}-db-sg",
            name=f"{SERVICE_NAME}-db-sg",
            description="Enable PostgreSQL access",
            vpc_id=self.networking.get_vpc_id(),
            ingress=[
                ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=self.db_cfg.port,
                    to_port=self.db_cfg.port,
                    security_groups=[backend_sg.id],
                ),
            ],
            egress=[
                {
                    "protocol": "-1",
                    "from_port": 0,
                    "to_port": 0,
                    "cidr_blocks": ["0.0.0.0/0"],
                },
            ],
        )

        db_subnet_group = rds.SubnetGroup(
            f"{SERVICE_NAME}-subnet-grp",
            subnet_ids=self.networking.get_subnet_ids(SubnetType.PRIVATE),
            description="Subnet group for my RDS instance",
        )

        self.random_password = random.RandomPassword(
            f"{SERVICE_NAME}-db-password",
            length=16,
            special=True,
            override_special="_-=,.!#$%^&*()+<>?{}[]",
        )

        self.cluster = rds.Cluster(
            f"{SERVICE_NAME}-cluster",
            database_name=self.db_cfg.db_name,
            engine=self.db_cfg.engine,
            engine_version=self.db_cfg.version,
            db_subnet_group_name=db_subnet_group.name,
            vpc_security_group_ids=[db_sg.id],
            master_username="db_user",
            master_password=self.random_password.result,
            skip_final_snapshot=True,
        )

        self.db_instance = rds.ClusterInstance(
            f"{SERVICE_NAME}-rds-instance",
            cluster_identifier=self.cluster.id,
            instance_class=self.db_cfg.family,
            engine=self.db_cfg.engine,
            engine_version=self.db_cfg.version,
            db_subnet_group_name=db_subnet_group.name,
        )

    def get_host(self) -> pulumi.Output:
        return self.cluster.endpoint

    def get_password(self) -> pulumi.Output:
        return self.random_password.result

    def get_db_instance(self) -> rds.ClusterInstance:
        return self.db_instance
