import pulumi_aws as aws

def setup_vpc():
    # Create a new VPC instead of using the default one
    vpc = aws.ec2.Vpc("main-vpc",
        cidr_block="10.0.0.0/16",
        enable_dns_hostnames=True,
        enable_dns_support=True,
        tags={
            "Name": "main-vpc"
        }
    )

    # Create an Internet Gateway
    internet_gateway = aws.ec2.InternetGateway("main-igw",
        vpc_id=vpc.id,
        tags={
            "Name": "main-internet-gateway"
        }
    )

    # Create a public subnet
    public_subnet = aws.ec2.Subnet("public-subnet",
        vpc_id=vpc.id,
        cidr_block="10.0.1.0/24",
        availability_zone="us-east-1a",  # You can make this configurable
        map_public_ip_on_launch=True,
        tags={
            "Name": "public-subnet"
        }
    )

    # Create a route table for public subnets
    public_route_table = aws.ec2.RouteTable("public-route-table",
        vpc_id=vpc.id,
        routes=[{
            "cidr_block": "0.0.0.0/0",
            "gateway_id": internet_gateway.id
        }],
        tags={
            "Name": "public-route-table"
        }
    )

    # Associate the public subnet with the route table
    public_route_table_association = aws.ec2.RouteTableAssociation("public-subnet-association",
        subnet_id=public_subnet.id,
        route_table_id=public_route_table.id
    )

    return {
        "vpc_id": vpc.id,
        "public_subnet_id": public_subnet.id,
        "internet_gateway_id": internet_gateway.id
    }
