import vpc.vpc as vpc
import sg.security as security 
import keys.keypair as keypair
import ec2.instance as instance
import output.outputs as outputs

# Orchestrate the infrastructure creation
vpc_info = vpc.setup_vpc()
sec_group = security.create_ssh_security_group(vpc_info["vpc_id"])
keys = keypair.generate_keypair()
ec2_instance = instance.launch_instance(vpc_info, sec_group, keys, instance_type="t2.micro")
outputs.export_outputs(ec2_instance, keys)
