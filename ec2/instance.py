import pulumi_aws as aws

def launch_instance(vpc_info, sec_group, keys, instance_type="t2.micro"):
    ami = aws.ec2.get_ami(
        most_recent=True,
        owners=["amazon"],
        filters=[
            {"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
            {"name": "virtualization-type", "values": ["hvm"]},
        ]
    )

    return aws.ec2.Instance(f"{instance_type}-instance",
        instance_type=instance_type,
        vpc_security_group_ids=[sec_group.id],
        ami=ami.id,
        key_name=keys["keypair"].key_name,
        subnet_id=vpc_info["public_subnet_id"],
        tags={"Name": "Pulumi-EC2"},
    )
