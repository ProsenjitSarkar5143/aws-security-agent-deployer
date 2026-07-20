"""Utility functions for the deployer."""

import time
from functools import wraps
from typing import Callable, Any, TypeVar, Optional
import logging
from src.exceptions import TimeoutException

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def retry(max_attempts: int = 3, delay: int = 60, backoff: float = 1.0):
    """Decorator for retrying failed operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            current_delay = delay
            last_exception = None
            
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    last_exception = e
                    
                    if attempt < max_attempts:
                        logger.warning(
                            f"Attempt {attempt} failed for {func.__name__}. "
                            f"Retrying in {current_delay}s...",
                            exc_info=True
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}",
                            exc_info=True
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


def timeout(seconds: int):
    """Decorator for adding timeout to operations.
    
    Args:
        seconds: Timeout in seconds
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import signal
            
            def timeout_handler(signum: int, frame: Any) -> None:
                raise TimeoutException(
                    f"Operation {func.__name__} timed out after {seconds}s"
                )
            
            # Set the signal handler and alarm
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                result = func(*args, **kwargs)
            finally:
                # Disable the alarm
                signal.alarm(0)
            
            return result
        
        return wrapper
    return decorator


def format_instance_info(instance: dict) -> str:
    """Format EC2 instance information for display.
    
    Args:
        instance: EC2 instance dictionary
        
    Returns:
        Formatted instance information
    """
    instance_id = instance.get("InstanceId", "N/A")
    state = instance.get("State", {}).get("Name", "N/A")
    instance_type = instance.get("InstanceType", "N/A")
    private_ip = instance.get("PrivateIpAddress", "N/A")
    tags = {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
    name = tags.get("Name", "N/A")
    
    return (
        f"Instance ID: {instance_id}, Name: {name}, "
        f"Type: {instance_type}, State: {state}, IP: {private_ip}"
    )


def validate_instance_id(instance_id: str) -> bool:
    """Validate EC2 instance ID format.
    
    Args:
        instance_id: Instance ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^i-[0-9a-f]{17}$|^i-[0-9a-f]{8}$'
    return bool(re.match(pattern, instance_id))


def validate_region(region: str) -> bool:
    """Validate AWS region format.
    
    Args:
        region: Region to validate
        
    Returns:
        True if valid, False otherwise
    """
    valid_regions = [
        'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
        'eu-west-1', 'eu-central-1', 'ap-southeast-1', 'ap-northeast-1',
    ]
    return region in valid_regions


def parse_tags(tag_string: str) -> dict:
    """Parse tag string into dictionary.
    
    Args:
        tag_string: Tag string in format "Key1:Value1,Key2:Value2"
        
    Returns:
        Dictionary of tags
    """
    tags = {}
    if not tag_string:
        return tags
    
    for tag in tag_string.split(","):
        if ":" not in tag:
            raise ValueError(f"Invalid tag format: {tag}")
        key, value = tag.split(":", 1)
        tags[key.strip()] = value.strip()
    
    return tags


def format_deployment_status(status: dict) -> str:
    """Format deployment status for display.
    
    Args:
        status: Deployment status dictionary
        
    Returns:
        Formatted status string
    """
    deployment_id = status.get("deployment_id", "N/A")
    agent = status.get("agent", "N/A")
    status_value = status.get("status", "N/A")
    successful = status.get("successful", 0)
    failed = status.get("failed", 0)
    total = status.get("total", 0)
    
    return (
        f"Deployment ID: {deployment_id}, Agent: {agent}, "
        f"Status: {status_value}, Successful: {successful}/{total}, "
        f"Failed: {failed}/{total}"
    )
