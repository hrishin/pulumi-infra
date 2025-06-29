import pulumi_aws as aws
import pulumi
from typing import Dict, Any, Optional

def launch_instance(vpc_info, sec_group, keys, ami="amzn2-ami-hvm-*-x86_64-gp2", instance_type="t2.micro", user_data: Optional[str] = None):
    """
    Launch an EC2 instance with optional user data for RAID configuration.
    
    Args:
        vpc_info: VPC information dictionary
        sec_group: Security group
        keys: Key pair information
        ami: AMI pattern to use
        instance_type: EC2 instance type
        user_data: Optional user data script (for RAID setup)
    
    Returns:
        EC2 instance resource
    """
    ami = aws.ec2.get_ami(
        most_recent=True,
        owners=["amazon"],
        filters=[
            {"name": "name", "values": [f"{ ami }"]},
            {"name": "virtualization-type", "values": ["hvm"]},
        ]
    )

    instance_args = {
        "instance_type": instance_type,
        "vpc_security_group_ids": [sec_group.id],
        "ami": ami.id,
        "key_name": keys["keypair"].key_name,
        "subnet_id": vpc_info["public_subnet_id"],
        "tags": {"Name": "Pulumi-EC2"},
        # Root volume configuration
        "root_block_device": {
            "volume_size": 8,
            "volume_type": "gp3",
            "delete_on_termination": True,
            "encrypted": True,
        }
    }
    
    # Add user data if provided (for RAID setup)
    if user_data:
        instance_args["user_data"] = user_data

    return aws.ec2.Instance(f"{instance_type}-instance", **instance_args)
