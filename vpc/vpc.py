import pulumi_aws as aws

def setup_vpc():
    vpc = aws.ec2.get_vpc(default=True)
    subnets = aws.ec2.get_subnets(filters=[{
        "name": "vpc-id",
        "values": [vpc.id],
    }])

    route_tables = aws.ec2.get_route_tables(filters=[{
        "name": "vpc-id",
        "values": [vpc.id],
    }])

    public_subnet_ids = []
    for rt_id in route_tables.ids:
        rt = aws.ec2.get_route_table(route_table_id=rt_id)
        has_igw = any(r.gateway_id and r.gateway_id.startswith("igw-") for r in rt.routes)
        if has_igw:
            for assoc in rt.associations:
                if assoc.subnet_id:
                    public_subnet_ids.append(assoc.subnet_id)

    return {
        "vpc_id": vpc.id,
        "public_subnet_id": public_subnet_ids[0] if public_subnet_ids else None
    }
