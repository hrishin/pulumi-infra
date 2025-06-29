import pulumi_aws as aws

def setup_vpc():
    az = "eu-west-2a"
    # Create a new VPC instead of using the default one
    vpc = aws.ec2.Vpc("production-vpc",
        cidr_block="172.16.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={
            "Name": "production-vpc",
            "Environment": "production",
            "ManagedBy": "pulumi"
        }
    )

    # Create an Internet Gateway
    internet_gateway = aws.ec2.InternetGateway("production-internet-gateway",
        vpc_id=vpc.id,
        tags={
            "Name": "production-internet-gateway",
            "Environment": "production",
            "ManagedBy": "pulumi"
        }
    )

    # Create a public subnet
    public_subnet = aws.ec2.Subnet("production-public-subnet",
        vpc_id=vpc.id,
        cidr_block="172.16.10.0/24",
        availability_zone=az,  # Updated to match the user's AWS region
        map_public_ip_on_launch=True,
        tags={
            "Name": "production-public-subnet",
            "Environment": "production",
            "Type": "public",
            "ManagedBy": "pulumi"
        }
    )

    # Create a route table for public subnets
    public_route_table = aws.ec2.RouteTable("production-public-route-table",
        vpc_id=vpc.id,
        routes=[{
            "cidr_block": "0.0.0.0/0",
            "gateway_id": internet_gateway.id
        }],
        tags={
            "Name": "production-public-route-table",
            "Environment": "production",
            "Type": "public",
            "ManagedBy": "pulumi"
        }
    )

    # Associate the public subnet with the route table
    public_route_table_association = aws.ec2.RouteTableAssociation("production-public-subnet-association",
        subnet_id=public_subnet.id,
        route_table_id=public_route_table.id
    )

    return {
        "vpc_id": vpc.id,
        "public_subnet_id": public_subnet.id,
        "internet_gateway_id": internet_gateway.id,
        "availability_zone": az
    }
