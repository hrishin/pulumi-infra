# EBS Volumes Module

This module provides functionality to create and manage Amazon EBS (Elastic Block Store) volumes using Pulumi.

## Features

- **Multiple Volume Creation**: Create multiple EBS volumes with custom configurations
- **Volume Attachment**: Automatically attach volumes to EC2 instances
- **Snapshot Support**: Create volumes from existing snapshots
- **IO-Optimized Volumes**: Create high-performance io2 volumes for demanding workloads
- **Encryption**: Support for encrypted volumes
- **Flexible Configuration**: Customizable volume types, sizes, and device names

## Functions

### `create_ebs_volumes(availability_zone, instance_id=None, volume_configs=None)`

Creates multiple EBS volumes and optionally attaches them to an EC2 instance.

**Parameters:**
- `availability_zone` (str): The AZ where volumes will be created
- `instance_id` (str, optional): EC2 instance ID to attach volumes to
- `volume_configs` (list, optional): List of volume configurations

**Returns:**
- Dictionary containing created volumes and attachments

**Example:**
```python
volume_configs = [
    {
        "name": "data-volume-1",
        "size": 20,
        "type": "gp3",
        "device_name": "/dev/sdf",
        "encrypted": True,
        "tags": {"Name": "Data-Volume-1", "Purpose": "Data Storage"}
    }
]

ebs_volumes = create_ebs_volumes(
    availability_zone="us-west-2a",
    instance_id=instance.id,
    volume_configs=volume_configs
)
```

### `create_ebs_volume_with_snapshot(snapshot_id, availability_zone, instance_id=None, device_name="/dev/sdf")`

Creates an EBS volume from a snapshot and optionally attaches it.

**Parameters:**
- `snapshot_id` (str): The snapshot ID to create volume from
- `availability_zone` (str): The AZ where volume will be created
- `instance_id` (str, optional): EC2 instance ID to attach volume to
- `device_name` (str): Device name for attachment

**Example:**
```python
snapshot_volume = create_ebs_volume_with_snapshot(
    snapshot_id="snap-1234567890abcdef0",
    availability_zone="us-west-2a",
    instance_id=instance.id,
    device_name="/dev/sdf"
)
```

### `create_io_optimized_volume(availability_zone, size=100, instance_id=None, device_name="/dev/sdf")`

Creates an IO-optimized EBS volume (io2) for high-performance workloads.

**Parameters:**
- `availability_zone` (str): The AZ where volume will be created
- `size` (int): Volume size in GB
- `instance_id` (str, optional): EC2 instance ID to attach volume to
- `device_name` (str): Device name for attachment

**Example:**
```python
io_volume = create_io_optimized_volume(
    availability_zone="us-west-2a",
    size=500,
    instance_id=instance.id,
    device_name="/dev/sdf"
)
```

## Volume Types Supported

- **gp3**: General Purpose SSD (recommended for most workloads)
- **gp2**: General Purpose SSD (legacy)
- **io2**: Provisioned IOPS SSD (high-performance)
- **io1**: Provisioned IOPS SSD (legacy)
- **st1**: Throughput Optimized HDD
- **sc1**: Cold HDD

## Device Names

Common device names for EBS volumes:
- `/dev/sdf` through `/dev/sdp` (Linux)
- `/dev/xvdf` through `/dev/xvdp` (Linux, alternative naming)
- `/dev/sd1` through `/dev/sd15` (Windows)

## Security Features

- **Encryption**: All volumes can be encrypted using AWS-managed keys
- **KMS Integration**: Support for customer-managed keys (can be extended)
- **IAM Policies**: Proper IAM permissions required for volume operations

## Best Practices

1. **Use gp3 for most workloads**: Better performance and cost than gp2
2. **Enable encryption**: Always encrypt sensitive data
3. **Use appropriate device names**: Avoid conflicts with existing devices
4. **Consider IOPS requirements**: Use io2 for high-performance needs
5. **Tag your volumes**: Use meaningful tags for cost tracking and management

## Integration with Main Application

The EBS module is integrated into the main Pulumi application (`__main__.py`) and creates:
- Two data volumes (20GB and 30GB) with gp3 type
- Automatic attachment to the EC2 instance
- Proper encryption and tagging

## Example Usage in Main Application

```python
# Create EBS volumes and attach them to the instance
ebs_volumes = ebs.create_ebs_volumes(
    availability_zone=vpc_info["availability_zone"],
    instance_id=ec2_instance.id,
    volume_configs=[
        {
            "name": "data-volume-1",
            "size": 20,
            "type": "gp3",
            "device_name": "/dev/sdf",
            "encrypted": True,
            "tags": {"Name": "Data-Volume-1", "Purpose": "Data Storage"}
        },
        {
            "name": "data-volume-2",
            "size": 30,
            "type": "gp3", 
            "device_name": "/dev/sdg",
            "encrypted": True,
            "tags": {"Name": "Data-Volume-2", "Purpose": "Backup Storage"}
        }
    ]
)
```

## Deployment

To deploy with EBS volumes:

```bash
pulumi up
```

The deployment will create:
1. VPC and networking infrastructure
2. EC2 instance
3. EBS volumes
4. Volume attachments

## Monitoring and Management

After deployment, you can:
- Monitor volume usage in AWS Console
- Create snapshots for backup
- Modify volume sizes (increase only)
- Change volume types
- Detach and reattach volumes

## Cost Considerations

- gp3 volumes are cost-effective for most workloads
- io2 volumes are more expensive but provide guaranteed IOPS
- Encrypted volumes have no additional cost
- Volume storage is charged per GB-month
- IOPS for io2 volumes are charged separately 