import pulumi
from typing import Dict, Any, List, Optional

def create_raid_user_data(raid_config: Dict[str, Any]) -> str:
    """
    Generate user data script for software RAID configuration.
    
    Args:
        raid_config: Configuration for RAID setup including:
            - raid_level: RAID level (0, 1, 5, 6, 10)
            - device_names: List of device names to use for RAID
            - mount_point: Where to mount the RAID array
            - filesystem: Filesystem type (ext4, xfs, etc.)
            - raid_device: RAID device name (e.g., /dev/md0)
    
    Returns:
        User data script as string
    """
    
    raid_level = raid_config.get("raid_level", 0)
    device_names = raid_config.get("device_names", [])
    mount_point = raid_config.get("mount_point", "/mnt/raid")
    filesystem = raid_config.get("filesystem", "ext4")
    raid_device = raid_config.get("raid_device", "/dev/md0")
    
    # Convert device names to actual block device paths
    # AWS typically maps /dev/sdf to /dev/xvdf, /dev/sdg to /dev/xvdg, etc.
    block_devices = []
    for device in device_names:
        # Convert /dev/sdf -> /dev/xvdf, /dev/sdg -> /dev/xvdg, etc.
        if device.startswith("/dev/sd"):
            block_device = device.replace("/dev/sd", "/dev/xvd")
            block_devices.append(block_device)
        else:
            block_devices.append(device)
    
    user_data_script = f"""#!/bin/bash
# Software RAID Configuration Script
set -e

# Wait for all EBS volumes to be attached and available
echo "Waiting for EBS volumes to be available..."
sleep 30

# Check if devices exist
for device in {' '.join(block_devices)}; do
    while [ ! -b $device ]; do
        echo "Waiting for device $device to be available..."
        sleep 5
    done
    echo "Device $device is available"
done

# Install mdadm if not present
if ! command -v mdadm &> /dev/null; then
    echo "Installing mdadm..."
    if command -v yum &> /dev/null; then
        yum install -y mdadm
    elif command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y mdadm
    fi
fi

# Create RAID array
echo "Creating RAID {raid_level} array..."
mdadm --create {raid_device} --level={raid_level} --raid-devices={len(block_devices)} {' '.join(block_devices)}

# Wait for RAID array to finish building
echo "Waiting for RAID array to finish building..."
while grep -q "resync" /proc/mdstat; do
    echo "RAID array is still building..."
    sleep 10
done

# Create filesystem
echo "Creating {filesystem} filesystem on RAID array..."
if [ "{filesystem}" = "xfs" ]; then
    mkfs.xfs {raid_device}
else
    mkfs.{filesystem} {raid_device}
fi

# Create mount point
echo "Creating mount point {mount_point}..."
mkdir -p {mount_point}

# Add to fstab for persistence
echo "Adding RAID array to fstab..."
echo "{raid_device} {mount_point} {filesystem} defaults,nofail 0 2" >> /etc/fstab

# Mount the RAID array
echo "Mounting RAID array..."
mount {raid_device} {mount_point}

# Set proper permissions
chmod 755 {mount_point}

echo "RAID {raid_level} setup complete!"
echo "RAID array mounted at {mount_point}"
echo "RAID status:"
cat /proc/mdstat
"""
    
    return user_data_script

def create_raid_monitoring_script(raid_device: str = "/dev/md0") -> str:
    """
    Generate a script to monitor RAID array health.
    
    Args:
        raid_device: The RAID device to monitor
    
    Returns:
        Monitoring script as string
    """
    
    monitoring_script = f"""#!/bin/bash
# RAID Monitoring Script

RAID_DEVICE="{raid_device}"
LOG_FILE="/var/log/raid-monitor.log"

# Function to log messages
log_message() {{
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}}

# Check RAID status
check_raid_status() {{
    if [ -e $RAID_DEVICE ]; then
        # Get RAID status
        RAID_STATUS=$(cat /proc/mdstat | grep -A 10 "md0")
        
        # Check for any failed devices
        if echo "$RAID_STATUS" | grep -q "\\[.*_.*\\]"; then
            log_message "WARNING: RAID array has failed devices!"
            log_message "RAID Status: $RAID_STATUS"
            return 1
        else
            log_message "RAID array is healthy"
            log_message "RAID Status: $RAID_STATUS"
            return 0
        fi
    else
        log_message "ERROR: RAID device $RAID_DEVICE not found!"
        return 1
    fi
}}

# Check disk space
check_disk_space() {{
    MOUNT_POINT=$(df $RAID_DEVICE | tail -1 | awk '{{print $6}}')
    if [ -n "$MOUNT_POINT" ]; then
        USAGE=$(df -h $MOUNT_POINT | tail -1 | awk '{{print $5}}' | sed 's/%//')
        if [ "$USAGE" -gt 80 ]; then
            log_message "WARNING: RAID array usage is ${{USAGE}}%"
        else
            log_message "RAID array usage: ${{USAGE}}%"
        fi
    fi
}}

# Main monitoring logic
log_message "Starting RAID monitoring check"
check_raid_status
check_disk_space
log_message "RAID monitoring check complete"
"""
    
    return monitoring_script

def get_raid_configuration(raid_level: int, volume_count: int) -> Dict[str, Any]:
    """
    Get recommended RAID configuration based on RAID level and volume count.
    
    Args:
        raid_level: RAID level (0, 1, 5, 6, 10)
        volume_count: Number of volumes available
    
    Returns:
        RAID configuration dictionary
    """
    
    configs = {
        0: {
            "description": "RAID 0 - Striping (no redundancy, maximum performance)",
            "min_volumes": 2,
            "usable_capacity": "100% of total capacity",
            "fault_tolerance": "None",
            "performance": "Excellent"
        },
        1: {
            "description": "RAID 1 - Mirroring (50% usable capacity, high redundancy)",
            "min_volumes": 2,
            "usable_capacity": "50% of total capacity",
            "fault_tolerance": "Can survive failure of 1 disk",
            "performance": "Good read, moderate write"
        },
        5: {
            "description": "RAID 5 - Distributed parity (good balance of capacity and redundancy)",
            "min_volumes": 3,
            "usable_capacity": "(n-1)/n of total capacity",
            "fault_tolerance": "Can survive failure of 1 disk",
            "performance": "Good read, moderate write"
        },
        6: {
            "description": "RAID 6 - Double distributed parity (high redundancy)",
            "min_volumes": 4,
            "usable_capacity": "(n-2)/n of total capacity",
            "fault_tolerance": "Can survive failure of 2 disks",
            "performance": "Good read, slower write"
        },
        10: {
            "description": "RAID 10 - Striped mirrors (excellent performance and redundancy)",
            "min_volumes": 4,
            "usable_capacity": "50% of total capacity",
            "fault_tolerance": "Can survive failure of 1 disk per mirror",
            "performance": "Excellent read and write"
        }
    }
    
    if raid_level not in configs:
        raise ValueError(f"Unsupported RAID level: {raid_level}")
    
    config = configs[raid_level]
    if volume_count < config["min_volumes"]:
        raise ValueError(f"RAID {raid_level} requires at least {config['min_volumes']} volumes, but only {volume_count} provided")
    
    return config

def create_logical_volume_user_data(device_names: List[str], mount_point: str = "/mnt/logical-volume", filesystem: str = "ext4") -> str:
    """
    Generate user data script for logical volume management without RAID.
    
    Args:
        device_names: List of device names to use for logical volume
        mount_point: Where to mount the logical volume
        filesystem: Filesystem type (ext4, xfs, etc.)
    
    Returns:
        User data script as string
    """
    
    # Convert device names to actual block device paths
    # AWS typically maps /dev/sdf to /dev/xvdf, /dev/sdg to /dev/xvdg, etc.
    block_devices = []
    for device in device_names:
        # Convert /dev/sdf -> /dev/xvdf, /dev/sdg -> /dev/xvdg, etc.
        if device.startswith("/dev/sd"):
            block_device = device.replace("/dev/sd", "/dev/xvd")
            block_devices.append(block_device)
        else:
            block_devices.append(device)
    
    # Create device list for LVM commands
    device_list = ' '.join(block_devices)
    
    user_data_script = f"""#!/bin/bash
# Logical Volume Management Configuration Script
set -e

# Wait for all EBS volumes to be attached and available
echo "Waiting for EBS volumes to be available..."
sleep 30

# Check if devices exist
for device in {device_list}; do
    while [ ! -b $device ]; do
        echo "Waiting for device $device to be available..."
        sleep 5
    done
    echo "Device $device is available"
done

# Install LVM tools if not present
if ! command -v pvcreate &> /dev/null; then
    echo "Installing LVM tools..."
    if command -v yum &> /dev/null; then
        yum install -y lvm2
    elif command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y lvm2
    fi
fi

# Create physical volumes
echo "Creating physical volumes..."
for device in {device_list}; do
    echo "Creating physical volume on $device"
    pvcreate $device
done

# Create volume group
echo "Creating volume group 'storage_vg'..."
vgcreate storage_vg {device_list}

# Create logical volume using all available space
echo "Creating logical volume 'storage_lv'..."
lvcreate -l 100%FREE -n storage_lv storage_vg

# Create filesystem
echo "Creating {filesystem} filesystem on logical volume..."
if [ "{filesystem}" = "xfs" ]; then
    mkfs.xfs /dev/storage_vg/storage_lv
else
    mkfs.{filesystem} /dev/storage_vg/storage_lv
fi

# Create mount point
echo "Creating mount point {mount_point}..."
mkdir -p {mount_point}

# Add to fstab for persistence
echo "Adding logical volume to fstab..."
echo "/dev/storage_vg/storage_lv {mount_point} {filesystem} defaults,nofail 0 2" >> /etc/fstab

# Mount the logical volume
echo "Mounting logical volume..."
mount /dev/storage_vg/storage_lv {mount_point}

# Set proper permissions
chmod 755 {mount_point}

echo "Logical volume setup complete!"
echo "Logical volume mounted at {mount_point}"
echo "Volume group information:"
vgs
echo "Logical volume information:"
lvs
echo "Physical volume information:"
pvs
"""
    
    return user_data_script 