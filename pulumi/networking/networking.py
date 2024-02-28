from typing import List

import pulumi
from pulumi import ResourceOptions
from pulumi_aws import ec2

from networking.subnet_type import SubnetType


class Networking:
    def __init__(self, config: pulumi.Config):
        self.vpc_name = config.get("vpc_name")
        self.add_nat = config.get_bool("add_nat", False)
        self.create_resources()

    def create_resources(self):
        self.vpc = ec2.Vpc(
            self.vpc_name, cidr_block="10.0.0.0/16", tags={"Name": self.vpc_name}
        )

        self.public_subnet_a = ec2.Subnet(
            "public-subnet-a",
            vpc_id=self.vpc.id,
            cidr_block="10.0.1.0/24",
            map_public_ip_on_launch=True,
            availability_zone="eu-west-1a",
            tags={
                "Name": "public-subnet-a",
            },
        )

        self.public_subnet_b = ec2.Subnet(
            "public-subnet-b",
            vpc_id=self.vpc.id,
            cidr_block="10.0.2.0/24",
            map_public_ip_on_launch=True,
            availability_zone="eu-west-1b",
            tags={
                "Name": "public-subnet-b",
            },
        )

        self.private_subnet = ec2.Subnet(
            "private-subnet",
            vpc_id=self.vpc.id,
            cidr_block="10.0.3.0/24",
            tags={
                "Name": "private-subnet",
            },
        )

        if self.add_nat:
            eip = ec2.Eip("my-eip")

            nat_gateway = ec2.NatGateway(
                f"{self.vpc_name}-nat-gateway",
                allocation_id=eip.id,
                subnet_id=self.public_subnet.id,
                tags={
                    "Name": f"{self.vpc_name}-nat-gateway",
                },
                opts=ResourceOptions(delete_before_replace=True),
            )

        igw = ec2.InternetGateway(
            f"{self.vpc_name}-igw",
            vpc_id=self.vpc.id,
            tags={
                "Name": f"{self.vpc_name}-igw",
            },
        )

        private_route_table = ec2.RouteTable(
            "private-route-table",
            vpc_id=self.vpc.id,
            tags={
                "Name": "private-route-table",
            },
        )

        if self.add_nat:
            ec2.Route(
                "nat-for-private-subnet",
                route_table_id=private_route_table.id,
                destination_cidr_block="0.0.0.0/0",
                nat_gateway_id=nat_gateway.id,
            )

        ec2.RouteTableAssociation(
            "private-rt-association",
            subnet_id=self.private_subnet.id,
            route_table_id=private_route_table.id,
        )

        public_route_table = ec2.RouteTable(
            "public-route-table",
            vpc_id=self.vpc.id,
            tags={
                "Name": "public-route-table",
            },
        )

        ec2.Route(
            "route-igw",
            route_table_id=public_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=igw.id,
        )

        ec2.RouteTableAssociation(
            "public-igw-association_a",
            subnet_id=self.public_subnet_a.id,
            route_table_id=public_route_table.id,
        )

        ec2.RouteTableAssociation(
            "public-igw-association_b",
            subnet_id=self.public_subnet_b.id,
            route_table_id=public_route_table.id,
        )

        self.security_group = ec2.SecurityGroup(
            f"{self.vpc_name}-sg",
            description="Allow all outbound",
            vpc_id=self.vpc.id,
            egress=[
                ec2.SecurityGroupEgressArgs(
                    from_port=0,
                    to_port=0,
                    protocol="-1",
                    cidr_blocks=["0.0.0.0/0"],
                    ipv6_cidr_blocks=["::/0"],
                )
            ],
            tags={
                "Name": f"{self.vpc_name}-sg",
            },
        )

    def get_vpc_id(self) -> ec2.Vpc.id:
        return self.vpc.id

    def get_subnet_ids(self, subnet_type: SubnetType) -> List[ec2.Subnet.id]:
        if subnet_type == SubnetType.PUBLIC:
            return [self.public_subnet_a.id, self.public_subnet_b.id]
        elif subnet_type == SubnetType.PRIVATE:
            return [self.private_subnet.id]
        else:
            raise ValueError(f"Invalid subnet type: {subnet_type}")