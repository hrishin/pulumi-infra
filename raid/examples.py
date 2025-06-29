"""
RAID Configuration Examples

This file contains example RAID configurations for different use cases.
"""

import raid.raid_config as raid_config

def get_raid_0_config():
    """
    RAID 0 configuration for maximum performance.
    Use case: High-performance workloads, temporary data, data processing.
    """
    return {
        "raid_level": 0,
        "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh"],
        "mount_point": "/mnt/fast-storage",
        "filesystem": "xfs",
        "raid_device": "/dev/md0",
        "description": "RAID 0 - Maximum performance, no redundancy"
    }

def get_raid_1_config():
    """
    RAID 1 configuration for high availability.
    Use case: Critical data, databases, application storage.
    """
    return {
        "raid_level": 1,
        "device_names": ["/dev/sdf", "/dev/sdg"],
        "mount_point": "/mnt/redundant-storage",
        "filesystem": "ext4",
        "raid_device": "/dev/md0",
        "description": "RAID 1 - High availability, 50% usable capacity"
    }

def get_raid_5_config():
    """
    RAID 5 configuration for cost-effective redundancy.
    Use case: File servers, backup storage, cost-sensitive environments.
    """
    return {
        "raid_level": 5,
        "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh", "/dev/sdi"],
        "mount_point": "/mnt/efficient-storage",
        "filesystem": "ext4",
        "raid_device": "/dev/md0",
        "description": "RAID 5 - Cost-effective redundancy, good read performance"
    }

def get_raid_6_config():
    """
    RAID 6 configuration for high redundancy.
    Use case: Critical data storage, long-term archives, high-reliability requirements.
    """
    return {
        "raid_level": 6,
        "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh", "/dev/sdi", "/dev/sdj"],
        "mount_point": "/mnt/secure-storage",
        "filesystem": "ext4",
        "raid_device": "/dev/md0",
        "description": "RAID 6 - High redundancy, can survive 2 disk failures"
    }

def get_raid_10_config():
    """
    RAID 10 configuration for best performance and redundancy.
    Use case: Production databases, high-performance applications, mission-critical systems.
    """
    return {
        "raid_level": 10,
        "device_names": ["/dev/sdf", "/dev/sdg", "/dev/sdh", "/dev/sdi"],
        "mount_point": "/mnt/production-storage",
        "filesystem": "ext4",
        "raid_device": "/dev/md0",
        "description": "RAID 10 - Best performance and redundancy combination"
    }

def get_custom_raid_config(raid_level: int, device_names: list, mount_point: str = "/mnt/raid", filesystem: str = "ext4"):
    """
    Create a custom RAID configuration.
    
    Args:
        raid_level: RAID level (0, 1, 5, 6, 10)
        device_names: List of device names
        mount_point: Mount point for the RAID array
        filesystem: Filesystem type
    
    Returns:
        RAID configuration dictionary
    """
    # Validate RAID configuration
    raid_config.get_raid_configuration(raid_level, len(device_names))
    
    return {
        "raid_level": raid_level,
        "device_names": device_names,
        "mount_point": mount_point,
        "filesystem": filesystem,
        "raid_device": "/dev/md0",
        "description": f"Custom RAID {raid_level} configuration"
    }

def get_volume_configs_for_raid(raid_level: int, volume_size: int = 10):
    """
    Generate EBS volume configurations for a specific RAID level.
    
    Args:
        raid_level: RAID level
        volume_size: Size of each volume in GB
    
    Returns:
        List of volume configurations
    """
    raid_info = raid_config.get_raid_configuration(raid_level, 2)  # Minimum volumes
    
    # Determine number of volumes based on RAID level
    if raid_level == 0:
        volume_count = 3  # Good performance with 3 volumes
    elif raid_level == 1:
        volume_count = 2
    elif raid_level == 5:
        volume_count = 4  # Good balance for RAID 5
    elif raid_level == 6:
        volume_count = 5  # Minimum 4, but 5 is better
    elif raid_level == 10:
        volume_count = 4
    else:
        raise ValueError(f"Unsupported RAID level: {raid_level}")
    
    # Generate device names
    device_names = []
    for i in range(volume_count):
        device_name = f"/dev/sd{chr(ord('c') + i)}"  # sdf, sdg, sdh, etc.
        device_names.append(device_name)
    
    # Generate volume configurations
    volume_configs = []
    for i, device_name in enumerate(device_names):
        volume_configs.append({
            "name": f"raid-volume-{i+1}",
            "size": volume_size,
            "type": "gp3",
            "device_name": device_name,
            "encrypted": True,
            "tags": {
                "Name": f"RAID-Volume-{i+1}",
                "Purpose": f"RAID {raid_level} Storage",
                "RAID_Level": str(raid_level)
            }
        })
    
    return volume_configs

# Example usage functions
def create_raid_0_setup():
    """Example: Create RAID 0 setup for high performance."""
    config = get_raid_0_config()
    user_data = raid_config.create_raid_user_data(config)
    volume_configs = get_volume_configs_for_raid(0, 20)
    return config, user_data, volume_configs

def create_raid_1_setup():
    """Example: Create RAID 1 setup for high availability."""
    config = get_raid_1_config()
    user_data = raid_config.create_raid_user_data(config)
    volume_configs = get_volume_configs_for_raid(1, 50)
    return config, user_data, volume_configs

def create_raid_10_setup():
    """Example: Create RAID 10 setup for production use."""
    config = get_raid_10_config()
    user_data = raid_config.create_raid_user_data(config)
    volume_configs = get_volume_configs_for_raid(10, 100)
    return config, user_data, volume_configs

def create_logical_volume_setup():
    """Example: Create logical volume setup without RAID."""
    device_names = ["/dev/sdc", "/dev/sdd"]  # Maps to /dev/xvdc and /dev/xvdd
    user_data = raid_config.create_logical_volume_user_data(
        device_names=device_names,
        mount_point="/mnt/logical-storage",
        filesystem="ext4"
    )
    volume_configs = get_volume_configs_for_logical_volume(device_names, 50)
    return device_names, user_data, volume_configs

def get_volume_configs_for_logical_volume(device_names: list, volume_size: int = 50):
    """
    Generate EBS volume configurations for logical volume management.
    
    Args:
        device_names: List of device names
        volume_size: Size of each volume in GB
    
    Returns:
        List of volume configurations
    """
    volume_configs = []
    for i, device_name in enumerate(device_names):
        volume_configs.append({
            "name": f"logical-volume-{i+1}",
            "size": volume_size,
            "type": "gp3",
            "device_name": device_name,
            "encrypted": True,
            "tags": {
                "Name": f"Logical-Volume-{i+1}",
                "Purpose": "Logical Volume Storage",
                "Storage_Type": "LVM"
            }
        })
    
    return volume_configs 