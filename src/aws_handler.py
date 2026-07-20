"""AWS EC2 and Systems Manager handler."""

import boto3
import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import BotoCoreError, ClientError
from src.config import AWSConfig
from src.exceptions import EC2Exception, SSMException, AWSException
from src.utils import retry

logger = logging.getLogger(__name__)


class AWSHandler:
    """Handles AWS EC2 and Systems Manager operations."""

    def __init__(self, config: AWSConfig):
        """Initialize AWS handler.
        
        Args:
            config: AWS configuration
        """
        self.config = config
        self.ec2_client = boto3.client(
            'ec2',
            region_name=config.region
        )
        self.ssm_client = boto3.client(
            'ssm',
            region_name=config.region
        )
        logger.info(f"AWS Handler initialized for region: {config.region}")

    @retry(max_attempts=3, delay=5)
    def get_instances(self, filters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Get EC2 instances matching filters.
        
        Args:
            filters: EC2 filters (e.g., [{'Name': 'instance-state-name', 'Values': ['running']}])
            
        Returns:
            List of EC2 instance dictionaries
            
        Raises:
            EC2Exception: If instance retrieval fails
        """
        try:
            if filters is None:
                filters = [{'Name': 'instance-state-name', 'Values': ['running']}]
            
            response = self.ec2_client.describe_instances(Filters=filters)
            instances = []
            
            for reservation in response['Reservations']:
                instances.extend(reservation['Instances'])
            
            logger.info(f"Retrieved {len(instances)} instances")
            return instances
        
        except ClientError as e:
            logger.error(f"Failed to get EC2 instances: {e}")
            raise EC2Exception(f"Failed to get EC2 instances: {e}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving instances: {e}")
            raise AWSException(f"Unexpected error retrieving instances: {e}")

    @retry(max_attempts=3, delay=5)
    def get_instance_by_id(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get EC2 instance by ID.
        
        Args:
            instance_id: EC2 instance ID
            
        Returns:
            Instance dictionary or None if not found
            
        Raises:
            EC2Exception: If retrieval fails
        """
        try:
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    if instance['InstanceId'] == instance_id:
                        logger.info(f"Retrieved instance: {instance_id}")
                        return instance
            
            return None
        
        except ClientError as e:
            logger.error(f"Failed to get instance {instance_id}: {e}")
            raise EC2Exception(f"Failed to get instance {instance_id}: {e}")

    @retry(max_attempts=3, delay=5)
    def get_instances_by_tag(self, tag_key: str, tag_value: str) -> List[Dict[str, Any]]:
        """Get EC2 instances by tag.
        
        Args:
            tag_key: Tag key
            tag_value: Tag value
            
        Returns:
            List of EC2 instances
            
        Raises:
            EC2Exception: If retrieval fails
        """
        filters = [
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]},
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
        return self.get_instances(filters=filters)

    @retry(max_attempts=3, delay=5)
    def send_command(
        self,
        instance_ids: List[str],
        document_name: str,
        parameters: Optional[Dict[str, List[str]]] = None,
        timeout_seconds: Optional[int] = None
    ) -> str:
        """Send Systems Manager command to instances.
        
        Args:
            instance_ids: List of EC2 instance IDs
            document_name: SSM document name
            parameters: Command parameters
            timeout_seconds: Command timeout
            
        Returns:
            Command ID
            
        Raises:
            SSMException: If command fails
        """
        try:
            if parameters is None:
                parameters = {}
            
            timeout = timeout_seconds or self.config.command_timeout
            
            response = self.ssm_client.send_command(
                InstanceIds=instance_ids,
                DocumentName=document_name,
                Parameters=parameters,
                TimeoutSeconds=timeout
            )
            
            command_id = response['Command']['CommandId']
            logger.info(
                f"Sent command {command_id} to {len(instance_ids)} instances "
                f"using document {document_name}"
            )
            return command_id
        
        except ClientError as e:
            logger.error(f"Failed to send command: {e}")
            raise SSMException(f"Failed to send command: {e}")

    @retry(max_attempts=3, delay=5)
    def get_command_status(self, command_id: str) -> Dict[str, Any]:
        """Get Systems Manager command status.
        
        Args:
            command_id: Command ID
            
        Returns:
            Command status dictionary
            
        Raises:
            SSMException: If retrieval fails
        """
        try:
            response = self.ssm_client.get_command_invocation_list(
                CommandId=command_id
            )
            
            status_summary = {
                'total': len(response['CommandInvocations']),
                'pending': 0,
                'success': 0,
                'failed': 0,
                'cancelled': 0,
                'invocations': []
            }
            
            for invocation in response['CommandInvocations']:
                status = invocation['Status']
                instance_id = invocation['InstanceId']
                
                if status == 'Pending':
                    status_summary['pending'] += 1
                elif status == 'Success':
                    status_summary['success'] += 1
                elif status == 'Failed':
                    status_summary['failed'] += 1
                elif status == 'Cancelled':
                    status_summary['cancelled'] += 1
                
                status_summary['invocations'].append({
                    'instance_id': instance_id,
                    'status': status,
                    'output': invocation.get('StandardOutputContent', '')
                })
            
            return status_summary
        
        except ClientError as e:
            logger.error(f"Failed to get command status: {e}")
            raise SSMException(f"Failed to get command status: {e}")

    @retry(max_attempts=3, delay=5)
    def get_command_output(self, command_id: str, instance_id: str) -> Dict[str, str]:
        """Get Systems Manager command output for a specific instance.
        
        Args:
            command_id: Command ID
            instance_id: Instance ID
            
        Returns:
            Dictionary with stdout and stderr
            
        Raises:
            SSMException: If retrieval fails
        """
        try:
            response = self.ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=instance_id
            )
            
            return {
                'stdout': response.get('StandardOutputContent', ''),
                'stderr': response.get('StandardErrorContent', ''),
                'status': response.get('Status', '')
            }
        
        except ClientError as e:
            logger.error(f"Failed to get command output: {e}")
            raise SSMException(f"Failed to get command output: {e}")

    @retry(max_attempts=3, delay=5)
    def create_tags(self, instance_ids: List[str], tags: Dict[str, str]) -> None:
        """Create tags on EC2 instances.
        
        Args:
            instance_ids: List of instance IDs
            tags: Dictionary of tags
            
        Raises:
            EC2Exception: If tagging fails
        """
        try:
            tag_list = [{'Key': k, 'Value': v} for k, v in tags.items()]
            self.ec2_client.create_tags(
                Resources=instance_ids,
                Tags=tag_list
            )
            logger.info(f"Tagged {len(instance_ids)} instances")
        
        except ClientError as e:
            logger.error(f"Failed to create tags: {e}")
            raise EC2Exception(f"Failed to create tags: {e}")

    @retry(max_attempts=3, delay=5)
    def get_instance_status(self, instance_id: str) -> Dict[str, Any]:
        """Get instance status details.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Status dictionary
            
        Raises:
            EC2Exception: If retrieval fails
        """
        try:
            response = self.ec2_client.describe_instance_status(
                InstanceIds=[instance_id]
            )
            
            if response['InstanceStatuses']:
                status = response['InstanceStatuses'][0]
                return {
                    'instance_id': instance_id,
                    'instance_status': status['InstanceStatus']['Status'],
                    'system_status': status['SystemStatus']['Status'],
                    'instance_state': status['InstanceState']['Name']
                }
            
            return None
        
        except ClientError as e:
            logger.error(f"Failed to get instance status: {e}")
            raise EC2Exception(f"Failed to get instance status: {e}")
