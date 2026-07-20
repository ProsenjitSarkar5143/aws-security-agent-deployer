"""AWS Systems Manager handler for command execution."""

import json
import logging
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.aws_handler import AWSHandler
from src.config import AWSConfig, DeploymentConfig
from src.exceptions import SSMException, TimeoutException
from src.utils import retry

logger = logging.getLogger(__name__)


class SSMManager:
    """Manages AWS Systems Manager operations."""

    def __init__(self, aws_config: AWSConfig, deployment_config: DeploymentConfig):
        """Initialize SSM Manager.
        
        Args:
            aws_config: AWS configuration
            deployment_config: Deployment configuration
        """
        self.aws_handler = AWSHandler(aws_config)
        self.config = deployment_config
        self.aws_config = aws_config
        logger.info("SSM Manager initialized")

    @retry(max_attempts=3, delay=5)
    def execute_deployment_command(
        self,
        instance_ids: List[str],
        script: str,
        deployment_id: str
    ) -> Dict[str, Any]:
        """Execute deployment command on instances.
        
        Args:
            instance_ids: List of EC2 instance IDs
            script: Script content to execute
            deployment_id: Deployment ID for tracking
            
        Returns:
            Deployment result dictionary
            
        Raises:
            SSMException: If execution fails
        """
        try:
            # Send command via Systems Manager
            parameters = {
                'commands': [script],
                'executionTimeout': [str(self.aws_config.command_timeout)]
            }
            
            command_id = self.aws_handler.send_command(
                instance_ids=instance_ids,
                document_name='AWS-RunShellScript',
                parameters=parameters
            )
            
            logger.info(f"Deployment command sent: {command_id}")
            
            # Wait for command completion
            result = self._wait_for_command_completion(
                command_id=command_id,
                instance_ids=instance_ids,
                deployment_id=deployment_id
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Deployment command execution failed: {e}")
            raise SSMException(f"Deployment command execution failed: {e}")

    def _wait_for_command_completion(
        self,
        command_id: str,
        instance_ids: List[str],
        deployment_id: str,
        max_wait_time: int = 600
    ) -> Dict[str, Any]:
        """Wait for command completion and collect results.
        
        Args:
            command_id: Command ID
            instance_ids: List of instance IDs
            deployment_id: Deployment ID
            max_wait_time: Maximum time to wait in seconds
            
        Returns:
            Deployment result dictionary
            
        Raises:
            TimeoutException: If command doesn't complete in time
        """
        start_time = time.time()
        poll_interval = 5  # seconds
        
        while time.time() - start_time < max_wait_time:
            try:
                status = self.aws_handler.get_command_status(command_id)
                
                # Check if all invocations are complete
                total = status['total']
                pending = status['pending']
                
                if pending == 0:  # All complete
                    return self._build_deployment_result(
                        command_id=command_id,
                        instance_ids=instance_ids,
                        deployment_id=deployment_id,
                        status=status
                    )
                
                logger.debug(
                    f"Command {command_id}: Pending={pending}/{total}, "
                    f"Success={status['success']}, Failed={status['failed']}"
                )
                
                time.sleep(poll_interval)
            
            except Exception as e:
                logger.error(f"Error checking command status: {e}")
                time.sleep(poll_interval)
        
        raise TimeoutException(
            f"Deployment command {command_id} did not complete within {max_wait_time}s"
        )

    def _build_deployment_result(
        self,
        command_id: str,
        instance_ids: List[str],
        deployment_id: str,
        status: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build deployment result from command status.
        
        Args:
            command_id: Command ID
            instance_ids: List of instance IDs
            deployment_id: Deployment ID
            status: Command status
            
        Returns:
            Deployment result dictionary
        """
        result = {
            'deployment_id': deployment_id,
            'command_id': command_id,
            'total_instances': len(instance_ids),
            'successful': status['success'],
            'failed': status['failed'],
            'cancelled': status['cancelled'],
            'status': 'Success' if status['failed'] == 0 else 'Partial',
            'invocations': []
        }
        
        # Collect detailed output for each instance
        for invocation in status['invocations']:
            output = self.aws_handler.get_command_output(
                command_id=command_id,
                instance_id=invocation['instance_id']
            )
            
            result['invocations'].append({
                'instance_id': invocation['instance_id'],
                'status': invocation['status'],
                'output': output
            })
        
        logger.info(f"Deployment result: {result['status']}")
        return result

    def execute_health_check(
        self,
        instance_ids: List[str],
        check_script: str
    ) -> Dict[str, Any]:
        """Execute health check on instances.
        
        Args:
            instance_ids: List of instance IDs
            check_script: Health check script
            
        Returns:
            Health check results
        """
        try:
            parameters = {
                'commands': [check_script],
                'executionTimeout': ['60']
            }
            
            command_id = self.aws_handler.send_command(
                instance_ids=instance_ids,
                document_name='AWS-RunShellScript',
                parameters=parameters,
                timeout_seconds=120
            )
            
            # Wait for health check completion
            time.sleep(10)  # Brief wait
            status = self.aws_handler.get_command_status(command_id)
            
            results = {
                'command_id': command_id,
                'total_instances': len(instance_ids),
                'healthy': status['success'],
                'unhealthy': status['failed'],
                'pending': status['pending'],
                'details': []
            }
            
            for invocation in status['invocations']:
                output = self.aws_handler.get_command_output(
                    command_id=command_id,
                    instance_id=invocation['instance_id']
                )
                
                results['details'].append({
                    'instance_id': invocation['instance_id'],
                    'status': invocation['status'],
                    'output': output['stdout']
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Health check execution failed: {e}")
            raise SSMException(f"Health check execution failed: {e}")
