from pulumi_aws import ec2


class ECSService:
    def __init__(self, vpc_id: ec2.Vpc.id):
        self.vpc_id = vpc_id
        self.create_resources()

    def create_resources(self):
        ec2.SecurityGroup(
            "lb-sg",
            name="lb-sg",
            description="Controls access to the ALB",
            vpc_id=self.vpc_id,
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
