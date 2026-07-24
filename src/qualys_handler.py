"""Qualys Cloud Agent deployment handler."""

import logging
import requests
from typing import Dict, List, Any, Optional
from requests.auth import HTTPBasicAuth
from src.config import QualysConfig
from src.exceptions import QualysException
from src.utils import retry

logger = logging.getLogger(__name__)


class QualysHandler:
    """Handles Qualys Cloud Agent deployment and management."""

    def __init__(self, config: QualysConfig):
        """Initialize Qualys handler.
        
        Args:
            config: Qualys configuration
        """
        self.config = config
        self.session = requests.Session()
        logger.info(f"Qualys Handler initialized for API: {config.api_url}")

    @retry(max_attempts=3, delay=10)
    def get_activation_code(self, username: str, password: str) -> str:
        """Get Qualys activation code for agent installation."""
        try:
            url = f"{self.config.api_url}/api/2.0/fo/cloud_agent/activation_code"
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                verify=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            if response.status_code != 200:
                raise QualysException(f"Failed to get activation code: {response.status_code}")
            logger.info("Successfully retrieved Qualys activation code")
            return response.text
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get activation code: {e}")
            raise QualysException(f"Failed to get activation code: {e}")

    def generate_installation_script(self, activation_code: str, os_type: str = "linux") -> str:
        """Generate Qualys agent installation script."""
        if os_type.lower() == "linux":
            script = f"""#!/bin/bash\nset -e\necho \"Starting Qualys Cloud Agent installation...\"\ncd /tmp\nwget https://repo.qualys.com/centos/qualys-cloud-agent.x86_64.rpm\nsudo rpm -ivh qualys-cloud-agent.x86_64.rpm\nsudo /opt/qualys/cloud-agent/bin/qualys-cloud-agent -a {activation_code}\nsudo systemctl enable qualys-cloud-agent\nsudo systemctl start qualys-cloud-agent\necho \"Qualys Cloud Agent installation completed\""""
        else:
            script = f"""powershell -Command \"Write-Host 'Installing Qualys'\"  """
        logger.info(f"Generated Qualys installation script for {os_type}")
        return script

    def generate_health_check_script(self, os_type: str = "linux") -> str:
        """Generate Qualys agent health check script."""
        if os_type.lower() == "linux":
            script = """#!/bin/bash\necho \"Checking Qualys Cloud Agent status...\"\nif systemctl is-active --quiet qualys-cloud-agent; then\n    echo \"Qualys Agent Status: RUNNING\"\n    exit 0\nelse\n    echo \"Qualys Agent Status: NOT RUNNING\"\n    exit 1\nfi"""
        else:
            script = """powershell -Command \"Write-Host 'Checking Qualys'\""""
        return script

    def generate_uninstall_script(self, os_type: str = "linux") -> str:
        """Generate Qualys agent uninstall script."""
        if os_type.lower() == "linux":
            script = """#!/bin/bash\necho \"Uninstalling Qualys Cloud Agent...\"\nsudo systemctl stop qualys-cloud-agent\nsudo systemctl disable qualys-cloud-agent\nsudo rpm -e qualys-cloud-agent"""
        else:
            script = """powershell -Command \"Write-Host 'Uninstalling Qualys'\""""
        return script
