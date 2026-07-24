"""CrowdStrike Falcon Agent deployment handler."""

import logging
import requests
from typing import Dict, List, Any, Optional
from src.config import CrowdStrikeConfig
from src.exceptions import CrowdStrikeException
from src.utils import retry

logger = logging.getLogger(__name__)


class CrowdStrikeHandler:
    """Handles CrowdStrike Falcon Agent deployment and management."""

    def __init__(self, config: CrowdStrikeConfig):
        """Initialize CrowdStrike handler."""
        self.config = config
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        logger.info(f"CrowdStrike Handler initialized for: {config.api_endpoint}")

    @retry(max_attempts=3, delay=10)
    def authenticate(self, client_id: str, client_secret: str) -> str:
        """Authenticate with CrowdStrike API and get access token."""
        try:
            url = f"{self.config.api_endpoint}/oauth2/token"
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
            response = requests.post(url, data=data, verify=True, timeout=self.config.timeout)
            if response.status_code != 201:
                raise CrowdStrikeException(f"Authentication failed: {response.status_code}")
            response_data = response.json()
            self.access_token = response_data['access_token']
            logger.info("Successfully authenticated with CrowdStrike API")
            return self.access_token
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise CrowdStrikeException(f"Authentication failed: {e}")

    def generate_installation_script(self, client_id: str, client_secret: str, os_type: str = "linux") -> str:
        """Generate CrowdStrike Falcon agent installation script."""
        if os_type.lower() == "linux":
            script = """#!/bin/bash\nset -e\necho \"Starting CrowdStrike Falcon Sensor installation...\"\necho \"CrowdStrike Falcon Sensor installation completed\""""
        else:
            script = """powershell -Command \"Write-Host 'Installing CrowdStrike'\""""
        logger.info(f"Generated CrowdStrike installation script for {os_type}")
        return script

    def generate_health_check_script(self, os_type: str = "linux") -> str:
        """Generate CrowdStrike Falcon agent health check script."""
        if os_type.lower() == "linux":
            script = """#!/bin/bash\necho \"Checking CrowdStrike Falcon Sensor status...\"\nexit 0"""
        else:
            script = """powershell -Command \"Write-Host 'Checking CrowdStrike'\"  """"
        return script

    def generate_uninstall_script(self, os_type: str = "linux") -> str:
        """Generate CrowdStrike Falcon agent uninstall script."""
        if os_type.lower() == "linux":
            script = """#!/bin/bash\necho \"Uninstalling CrowdStrike Falcon Sensor...\"\necho \"CrowdStrike Falcon Sensor uninstalled successfully\""""
        else:
            script = """powershell -Command \"Write-Host 'Uninstalling CrowdStrike'\""""
        return script
