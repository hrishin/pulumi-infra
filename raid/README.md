# Software RAID Configuration for EBS Volumes

This module provides software RAID configuration for EBS volumes attached to EC2 instances using Linux's `mdadm` utility.

## Features

- **Multiple RAID Levels**: Support for RAID 0, 1, 5, 6, and 10
- **Automatic Setup**: User data scripts automatically configure RAID arrays
- **Monitoring**: Built-in RAID health monitoring scripts
- **Flexible Configuration**: Customizable mount points, filesystems, and device mappings

## RAID Levels Supported

### RAID 0 - Striping
- **Performance**: Excellent (no redundancy overhead)
- **Fault Tolerance**: None
- **Usable Capacity**: 100% of total capacity
- **Minimum Volumes**: 2
- **Use Case**: High-performance workloads where data loss is acceptable

### RAID 1 - Mirroring
- **Performance**: Good read, moderate write
- **Fault Tolerance**: Can survive failure of 1 disk
- **Usable Capacity**: 50% of total capacity
- **Minimum Volumes**: 2
- **Use Case**: High availability with good read performance

### RAID 5 - Distributed Parity
- **Performance**: Good read, moderate write
- **Fault Tolerance**: Can survive failure of 1 disk
- **Usable Capacity**: (n-1)/n of total capacity
- **Minimum Volumes**: 3
- **Use Case**: Good balance of capacity and redundancy

### RAID 6 - Double Distributed Parity
- **Performance**: Good read, slower write
- **Fault Tolerance**: Can survive failure of 2 disks
- **Usable Capacity**: (n-2)/n of total capacity
- **Minimum Volumes**: 4
- **Use Case**: High redundancy for critical data

### RAID 10 - Striped Mirrors
- **Performance**: Excellent read and write
- **Fault Tolerance**: Can survive failure of 1 disk per mirror
- **Usable Capacity**: 50% of total capacity
- **Minimum Volumes**: 4
- **Use Case**: Best performance and redundancy combination

## Usage

### Basic RAID 1 Setup

```python
import raid.raid_config as raid_config

# Configure RAID 1 for two EBS volumes
raid_setup = {
    "raid_level": 1,
    "device_names": ["/dev/sdf", "/dev/sdg"],
    "mount_point": "/mnt/raid",
    "filesystem": "ext4",
    "raid_device": "/dev/md0"
}

# Generate user data script
raid_user_data = raid_config.create_raid_user_data(raid_setup)

# Use in EC2 instance creation
ec2_instance = instance.launch_instance(
    vpc_info, 
    sec_group, 
    keys, 
    user_data=raid_user_data
)
```

### RAID 0 for Performance

```python
raid_setup = {
    "raid_level": 0,
    "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh"],
    "mount_point": "/mnt/fast-storage",
    "filesystem": "xfs",
    "raid_device": "/dev/md0"
}
```

### RAID 10 for Best Performance and Redundancy

```python
raid_setup = {
    "raid_level": 10,
    "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh", "/dev/sdi"],
    "mount_point": "/mnt/production-data",
    "filesystem": "ext4",
    "raid_device": "/dev/md0"
}
```

## Device Name Mapping

AWS automatically maps device names as follows:
- `/dev/sdf` → `/dev/xvdf`
- `/dev/sdg` → `/dev/xvdg`
- `/dev/sdh` → `/dev/xvdh`
- etc.

The RAID configuration script automatically handles this mapping.

## Monitoring

The module includes a monitoring script that can be used to check RAID health:

```python
monitoring_script = raid_config.create_raid_monitoring_script("/dev/md0")
```

This script checks:
- RAID array status
- Failed devices
- Disk space usage
- Overall health

## Best Practices

1. **RAID Level Selection**:
   - Use RAID 1 for critical data requiring high availability
   - Use RAID 0 for temporary data requiring maximum performance
   - Use RAID 10 for production workloads requiring both performance and redundancy
   - Use RAID 5/6 for cost-effective redundancy with larger volumes

2. **Volume Sizing**:
   - For RAID 1: Use identical volume sizes
   - For RAID 0: Volumes can be different sizes (smallest volume determines stripe size)
   - For RAID 5/6: Use identical volume sizes for optimal performance

3. **Monitoring**:
   - Set up regular monitoring of RAID array health
   - Monitor disk space usage
   - Set up alerts for failed devices

4. **Backup Strategy**:
   - RAID is not a backup solution
   - Implement regular backups of data on RAID arrays
   - Consider using EBS snapshots for backup

## Troubleshooting

### Common Issues

1. **Devices Not Available**: The script waits for devices to be available, but if issues persist, check EBS volume attachments.

2. **RAID Array Building**: RAID arrays take time to build, especially for larger volumes. The script waits for completion.

3. **Filesystem Issues**: Ensure the filesystem type is supported by your OS (ext4, xfs, etc.).

### Manual RAID Management

If you need to manage RAID arrays manually:

```bash
# Check RAID status
cat /proc/mdstat

# Check RAID array details
mdadm --detail /dev/md0

# Add a new device to RAID array
mdadm --add /dev/md0 /dev/xvdi

# Remove a failed device
mdadm --remove /dev/md0 /dev/xvdf

# Stop RAID array
mdadm --stop /dev/md0
```

## Security Considerations

- RAID arrays are automatically encrypted if EBS volumes are encrypted
- Ensure proper file permissions on mount points
- Consider using IAM roles for EC2 instances to manage EBS volumes
- Monitor access to RAID arrays and mount points 