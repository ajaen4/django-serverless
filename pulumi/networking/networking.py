from pulumi import ResourceOptions
from pulumi_aws import ec2

from input_schemas import VPCCfg, SubnetType


class Networking:
    def __init__(self, vpc_cfg: VPCCfg):
        self.vpc_name = vpc_cfg.vpc_name
        self.add_nat = vpc_cfg.add_nat
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

        self.private_subnet_a = ec2.Subnet(
            "private-subnet-a",
            vpc_id=self.vpc.id,
            cidr_block="10.0.3.0/24",
            tags={
                "Name": "private-subnet-a",
            },
            availability_zone="eu-west-1a",
        )

        self.private_subnet_b = ec2.Subnet(
            "private-subnet-b",
            vpc_id=self.vpc.id,
            cidr_block="10.0.4.0/24",
            tags={
                "Name": "private-subnet-b",
            },
            availability_zone="eu-west-1b",
        )

        if self.add_nat:
            eip = ec2.Eip("my-eip")

            nat_gateway = ec2.NatGateway(
                f"{self.vpc_name}-nat-gateway",
                allocation_id=eip.id,
                subnet_id=self.public_subnet_a.id,
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
            "private-rt-association-a",
            subnet_id=self.private_subnet_a.id,
            route_table_id=private_route_table.id,
        )

        ec2.RouteTableAssociation(
            "private-rt-association-b",
            subnet_id=self.private_subnet_b.id,
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

    def get_vpc_id(self) -> ec2.Vpc.id:
        return self.vpc.id

    def get_subnet_ids(self, subnet_type: SubnetType) -> list[ec2.Subnet.id]:
        if subnet_type == SubnetType.PUBLIC:
            return [self.public_subnet_a.id, self.public_subnet_b.id]
        elif subnet_type == SubnetType.PRIVATE:
            return [self.private_subnet_a.id, self.private_subnet_b.id]
        else:
            raise ValueError(f"Invalid subnet type: {subnet_type}")
