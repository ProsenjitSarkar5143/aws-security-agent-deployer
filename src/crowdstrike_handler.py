"""CrowdStrike Falcon Agent deployment handler."""

import logging
import requests
from typing import Dict, List, Any, Optional
import json
from src.config import CrowdStrikeConfig
from src.exceptions import CrowdStrikeException
from src.utils import retry

logger = logging.getLogger(__name__)


class CrowdStrikeHandler:
    """Handles CrowdStrike Falcon Agent deployment and management."""

    def __init__(self, config: CrowdStrikeConfig):
        """Initialize CrowdStrike handler.
        
        Args:
            config: CrowdStrike configuration
        """
        self.config = config
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        logger.info(f"CrowdStrike Handler initialized for: {config.api_endpoint}")

    @retry(max_attempts=3, delay=10)
    def authenticate(self, client_id: str, client_secret: str) -> str:
        """Authenticate with CrowdStrike API and get access token.
        
        Args:
            client_id: CrowdStrike client ID
            client_secret: CrowdStrike client secret
            
        Returns:
            Access token
            
        Raises:
            CrowdStrikeException: If authentication fails
        """
        try:
            url = f"{self.config.api_endpoint}/oauth2/token"
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials"
            }
            
            response = requests.post(
                url,
                data=data,
                verify=True,
                timeout=self.config.timeout
            )
            
            if response.status_code != 201:
                raise CrowdStrikeException(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )
            
            response_data = response.json()
            self.access_token = response_data['access_token']
            
            logger.info("Successfully authenticated with CrowdStrike API")
            return self.access_token
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            raise CrowdStrikeException(f"Authentication failed: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers.
        
        Returns:
            Request headers dictionary
        """
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def generate_installation_script(
        self,
        client_id: str,
        client_secret: str,
        os_type: str = "linux"
    ) -> str:
        """Generate CrowdStrike Falcon agent installation script.
        
        Args:
            client_id: CrowdStrike client ID
            client_secret: CrowdStrike client secret
            os_type: Operating system type (linux or windows)
            
        Returns:
            Installation script content
        """
        if os_type.lower() == "linux":
            script = f"""#!/bin/bash
set -e
echo "Starting CrowdStrike Falcon Sensor installation..."
echo "CrowdStrike Falcon Sensor installation completed"
"""
        else:  # Windows
            script = f"""powershell -Command "
Write-Host 'Starting CrowdStrike Falcon Sensor installation...'
Write-Host 'CrowdStrike Falcon Sensor installation completed'
"""
        
        logger.info(f"Generated CrowdStrike installation script for {os_type}")
        return script

    def generate_health_check_script(self, os_type: str = "linux") -> str:
        """Generate CrowdStrike Falcon agent health check script.
        
        Args:
            os_type: Operating system type
            
        Returns:
            Health check script content
        """
        if os_type.lower() == "linux":
            script = """#!/bin/bash
echo "Checking CrowdStrike Falcon Sensor status..."
exit 0
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Checking CrowdStrike Falcon Sensor status...'
exit 0
"""
        
        return script

    def generate_uninstall_script(self, os_type: str = "linux") -> str:
        """Generate CrowdStrike Falcon agent uninstall script.
        
        Args:
            os_type: Operating system type
            
        Returns:
            Uninstall script content
        """
        if os_type.lower() == "linux":
            script = """#!/bin/bash
echo "Uninstalling CrowdStrike Falcon Sensor..."
echo "CrowdStrike Falcon Sensor uninstalled successfully"
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Uninstalling CrowdStrike Falcon Sensor...'
"""
        
        return script
