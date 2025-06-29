import pulumi_aws as aws

def launch_instance(vpc_info, sec_group, keys, ami="amzn2-ami-hvm-*-x86_64-gp2", instance_type="t2.micro"):
    ami = aws.ec2.get_ami(
        most_recent=True,
        owners=["amazon"],
        filters=[
            {"name": "name", "values": [f"{ ami }"]},
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
        # EBS block device configuration
        ebs_block_devices=[{
            "device_name": "/dev/xvdc",
            "volume_size": 10,
            "volume_type": "gp3",
            "delete_on_termination": False,
            "encrypted": False,
        },{
            "device_name": "/dev/xvdd",
            "volume_size": 10,
            "volume_type": "gp3",
            "delete_on_termination": False,
            "encrypted": False,
        }],
    )
