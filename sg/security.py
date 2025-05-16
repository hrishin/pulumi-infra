import pulumi_aws as aws

def create_ssh_security_group(vpc_id):
    return aws.ec2.SecurityGroup("web-secgrp",
        description="Enable SSH access",
        vpc_id=vpc_id,
        ingress=[{
            "protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"],
        }],
        egress=[{
            "protocol": "-1", "from_port": 0, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"],
        }]
    )
