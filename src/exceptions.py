"""Custom exceptions for AWS Security Agent Deployer."""


class DeployerException(Exception):
    """Base exception for all deployer errors."""
    pass


class AWSException(DeployerException):
    """Exception raised for AWS-related errors."""
    pass


class EC2Exception(AWSException):
    """Exception raised for EC2 operation errors."""
    pass


class SSMException(AWSException):
    """Exception raised for Systems Manager errors."""
    pass


class LambdaException(AWSException):
    """Exception raised for Lambda operation errors."""
    pass


class AgentDeploymentException(DeployerException):
    """Exception raised for agent deployment errors."""
    pass


class QualysException(AgentDeploymentException):
    """Exception raised for Qualys-specific errors."""
    pass


class CrowdStrikeException(AgentDeploymentException):
    """Exception raised for CrowdStrike-specific errors."""
    pass


class ConfigurationException(DeployerException):
    """Exception raised for configuration errors."""
    pass


class ValidationException(DeployerException):
    """Exception raised for validation errors."""
    pass


class CredentialsException(DeployerException):
    """Exception raised for credential-related errors."""
    pass


class TimeoutException(DeployerException):
    """Exception raised when an operation times out."""
    pass


class HealthCheckException(DeployerException):
    """Exception raised for health check failures."""
    pass


class RollbackException(DeployerException):
    """Exception raised for rollback operation failures."""
    pass
