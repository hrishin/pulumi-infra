import pulumi_aws as aws
import pulumi
from typing import Dict, Any, Optional, List

def create_ebs_volumes(availability_zone: str, instance_id: Optional[str] = None, volume_configs: Optional[List[Dict[str, Any]]] = None):
    """
    Create EBS volumes and optionally attach them to an EC2 instance.
    
    Args:
        availability_zone: The AZ where volumes will be created
        instance_id: Optional EC2 instance ID to attach volumes to
        volume_configs: List of volume configurations
    
    Returns:
        Dictionary containing created volumes and attachments
    """
    
    # Default volume configurations if none provided
    if volume_configs is None:
        volume_configs = [
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
    
    volumes: Dict[str, aws.ebs.Volume] = {}
    attachments: Dict[str, aws.ec2.VolumeAttachment] = {}
    
    # Create EBS volumes
    for config in volume_configs:
        volume = aws.ebs.Volume(
            config["name"],
            availability_zone=availability_zone,
            size=config["size"],
            type=config["type"],
            encrypted=config.get("encrypted", False),
            tags=config.get("tags", {})
        )
        volumes[config["name"]] = volume
        
        # Attach volume to instance if instance_id is provided
        if instance_id:
            attachment = aws.ec2.VolumeAttachment(
                f"{config['name']}-attachment",
                device_name=config["device_name"],
                volume_id=volume.id,
                instance_id=instance_id
            )
            attachments[f"{config['name']}-attachment"] = attachment
    
    return {
        "volumes": volumes,
        "attachments": attachments
    }

def create_ebs_volume_with_snapshot(snapshot_id: str, availability_zone: str, instance_id: Optional[str] = None, device_name: str = "/dev/sdf"):
    """
    Create an EBS volume from a snapshot and optionally attach it.
    
    Args:
        snapshot_id: The snapshot ID to create volume from
        availability_zone: The AZ where volume will be created
        instance_id: Optional EC2 instance ID to attach volume to
        device_name: Device name for attachment
    
    Returns:
        Dictionary containing created volume and attachment
    """
    
    volume = aws.ebs.Volume(
        "snapshot-volume",
        availability_zone=availability_zone,
        snapshot_id=snapshot_id,
        type="gp3",
        encrypted=True,
        tags={"Name": "Snapshot-Volume", "Source": f"snapshot-{snapshot_id}"}
    )
    
    result: Dict[str, Any] = {"volume": volume}
    
    if instance_id:
        attachment = aws.ec2.VolumeAttachment(
            "snapshot-volume-attachment",
            device_name=device_name,
            volume_id=volume.id,
            instance_id=instance_id
        )
        result["attachment"] = attachment
    
    return result

def create_io_optimized_volume(availability_zone: str, size: int = 100, instance_id: Optional[str] = None, device_name: str = "/dev/sdf"):
    """
    Create an IO-optimized EBS volume (io2) for high-performance workloads.
    
    Args:
        availability_zone: The AZ where volume will be created
        size: Volume size in GB
        instance_id: Optional EC2 instance ID to attach volume to
        device_name: Device name for attachment
    
    Returns:
        Dictionary containing created volume and attachment
    """
    
    volume = aws.ebs.Volume(
        "io-optimized-volume",
        availability_zone=availability_zone,
        size=size,
        type="io2",
        iops=3000,  # IO2 volumes require IOPS specification
        encrypted=True,
        tags={"Name": "IO-Optimized-Volume", "Type": "io2"}
    )
    
    result: Dict[str, Any] = {"volume": volume}
    
    if instance_id:
        attachment = aws.ec2.VolumeAttachment(
            "io-optimized-volume-attachment",
            device_name=device_name,
            volume_id=volume.id,
            instance_id=instance_id
        )
        result["attachment"] = attachment
    
    return result 