"""Configuration management for the deployer application."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from pydantic_settings import BaseSettings
from pydantic import Field
from src.exceptions import ConfigurationException


class AWSConfig(BaseSettings):
    """AWS configuration."""
    region: str = Field(default="us-east-1")
    profile: str = Field(default="default")
    ssm_document_name: str = Field(default="SecurityAgentDeployment")
    max_concurrent_instances: int = Field(default=10)
    command_timeout: int = Field(default=300)
    verify_ssl: bool = Field(default=True)


class QualysConfig(BaseSettings):
    """Qualys configuration."""
    api_url: str
    verify_ssl: bool = Field(default=True)
    timeout: int = Field(default=300)
    retry_attempts: int = Field(default=3)
    retry_delay: int = Field(default=60)
    agent_url: Optional[str] = Field(default="")


class CrowdStrikeConfig(BaseSettings):
    """CrowdStrike configuration."""
    api_endpoint: str
    timeout: int = Field(default=300)
    retry_attempts: int = Field(default=3)
    retry_delay: int = Field(default=60)
    sensor_url: Optional[str] = Field(default="")


class DeploymentConfig(BaseSettings):
    """Deployment configuration."""
    mode: str = Field(default="lambda")  # lambda or ec2
    parallel_instances: int = Field(default=5)
    retry_attempts: int = Field(default=3)
    retry_delay: int = Field(default=60)
    health_check_interval: int = Field(default=300)
    auto_rollback_on_failure: bool = Field(default=True)
    failure_threshold: int = Field(default=30)
    dry_run: bool = Field(default=False)


class LambdaConfig(BaseSettings):
    """Lambda configuration."""
    function_name: str = Field(default="security-agent-deployer")
    memory_size: int = Field(default=512)
    timeout: int = Field(default=600)
    reserved_concurrency: int = Field(default=10)
    vpc_mode: bool = Field(default=False)


class EC2Config(BaseSettings):
    """EC2 configuration."""
    instance_type: str = Field(default="t3.medium")
    volume_size: int = Field(default=30)
    key_pair_name: str = Field(default="deployer-key")
    security_group: str = Field(default="deployer-sg")
    subnet_id: Optional[str] = Field(default="")
    associate_public_ip: bool = Field(default=True)
    monitoring_enabled: bool = Field(default=True)


class LoggingConfig(BaseSettings):
    """Logging configuration."""
    level: str = Field(default="INFO")
    format: str = Field(default="json")
    cloudwatch_enabled: bool = Field(default=True)
    log_group_name: str = Field(default="/aws/security-agent-deployer")
    retention_days: int = Field(default=30)
    file_path: str = Field(default="logs/deployment.log")


class ConfigManager:
    """Manages application configuration."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path or os.getenv("CONFIG_PATH", "config.yaml")
        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self) -> None:
        """Load configuration from YAML file."""
        if not Path(self.config_path).exists():
            raise ConfigurationException(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationException(f"Failed to parse configuration file: {e}")
        except Exception as e:
            raise ConfigurationException(f"Failed to load configuration: {e}")

    def get_aws_config(self) -> AWSConfig:
        """Get AWS configuration."""
        return AWSConfig(**self.config.get("aws", {}))

    def get_qualys_config(self) -> QualysConfig:
        """Get Qualys configuration."""
        qualys_config = self.config.get("qualys", {})
        qualys_config["api_url"] = os.getenv("QUALYS_API_URL", qualys_config.get("api_url", ""))
        return QualysConfig(**qualys_config)

    def get_crowdstrike_config(self) -> CrowdStrikeConfig:
        """Get CrowdStrike configuration."""
        cs_config = self.config.get("crowdstrike", {})
        cs_config["api_endpoint"] = os.getenv("CROWDSTRIKE_API_ENDPOINT", cs_config.get("api_endpoint", ""))
        return CrowdStrikeConfig(**cs_config)

    def get_deployment_config(self) -> DeploymentConfig:
        """Get deployment configuration."""
        return DeploymentConfig(**self.config.get("deployment", {}))

    def get_lambda_config(self) -> LambdaConfig:
        """Get Lambda configuration."""
        return LambdaConfig(**self.config.get("lambda", {}))

    def get_ec2_config(self) -> EC2Config:
        """Get EC2 configuration."""
        return EC2Config(**self.config.get("ec2", {}))

    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return LoggingConfig(**self.config.get("logging", {}))
