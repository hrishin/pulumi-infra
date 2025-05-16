import subprocess
import pulumi_aws as aws

PRIVATE_KEY_PATH = "./ec2_key"
PUBLIC_KEY_PATH = PRIVATE_KEY_PATH + ".pub"

def generate_keypair():
    subprocess.run(["ssh-keygen", "-t", "rsa", "-b", "2048", "-f", PRIVATE_KEY_PATH, "-N", ""])
    
    with open(PRIVATE_KEY_PATH, "r") as f:
        private_key = f.read()
    with open(PUBLIC_KEY_PATH, "r") as f:
        public_key = f.read()

    keypair = aws.ec2.KeyPair("ec2-keypair", public_key=public_key)

    return {
        "keypair": keypair,
        "private_key": private_key,
        "ssh_user": "ec2-user"
    }
