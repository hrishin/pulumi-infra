import pulumi

def export_outputs(instance, keys):
    pulumi.export("public_ip", instance.public_ip)
    pulumi.export("public_dns", instance.public_dns)
    pulumi.export("ssh_private_key", pulumi.Output.secret(keys["private_key"]))
    pulumi.export("ssh_user", pulumi.Output.secret(keys["ssh_user"]))
