import vpc.vpc as vpc
import sg.security as security 
import keys.keypair as keypair
import ec2.instance as instance
import ebs.volumes as ebs
import output.outputs as outputs
import raid.raid_config as raid_config
import raid.examples as raid_examples
import pulumi
import sys

# Orchestrate the infrastructure creation
vpc_info = vpc.setup_vpc()
sec_group = security.create_ssh_security_group(vpc_info["vpc_id"])
keys = keypair.generate_keypair()

# Create logical volume configuration for /dev/xvdc and /dev/xvdd
device_names, logical_volume_user_data, volume_configs = raid_examples.create_logical_volume_setup()

# Create EBS volumes and attach them to the instance
def create_ebs_volumes_with_instance(availability_zone, instance_id):
    return ebs.create_ebs_volumes(
        availability_zone=availability_zone,
        instance_id=instance_id,
        volume_configs=volume_configs
    )

# Launch EC2 instance with logical volume configuration
ec2_instance = instance.launch_instance(
    vpc_info, 
    sec_group, 
    keys, 
    instance_type="t2.micro",
    user_data=logical_volume_user_data
)

ebs_volumes = pulumi.Output.all(
    vpc_info["availability_zone"], 
    ec2_instance.id
).apply(lambda args: create_ebs_volumes_with_instance(args[0], args[1]))

# Export logical volume information
pulumi.export("logical_volume_devices", device_names)
pulumi.export("logical_volume_mount_point", "/mnt/logical-storage")
pulumi.export("logical_volume_filesystem", "ext4")
pulumi.export("logical_volume_description", "Logical Volume Management without RAID")

outputs.export_outputs(ec2_instance, keys, ebs_volumes)
