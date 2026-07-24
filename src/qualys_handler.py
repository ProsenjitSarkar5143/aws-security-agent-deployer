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
        """Get Qualys activation code for agent installation.
        
        Args:
            username: Qualys API username
            password: Qualys API password
            
        Returns:
            Activation code
            
        Raises:
            QualysException: If authentication fails
        """
        try:
            url = f"{self.config.api_url}/api/2.0/fo/cloud_agent/activation_code"
            
            response = requests.get(
                url,
                auth=HTTPBasicAuth(username, password),
                verify=self.config.verify_ssl,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                raise QualysException(
                    f"Failed to get activation code: {response.status_code} - {response.text}"
                )
            
            # Parse XML response to extract activation code
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            activation_code = root.findtext('.//CODE')
            
            if not activation_code:
                raise QualysException("Activation code not found in response")
            
            logger.info("Successfully retrieved Qualys activation code")
            return activation_code
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get activation code: {e}")
            raise QualysException(f"Failed to get activation code: {e}")

    def generate_installation_script(self, activation_code: str, os_type: str = "linux") -> str:
        """Generate Qualys agent installation script.
        
        Args:
            activation_code: Qualys activation code
            os_type: Operating system type (linux or windows)
            
        Returns:
            Installation script content
        """
        if os_type.lower() == "linux":
            script = f"""#!/bin/bash
set -e

echo "Starting Qualys Cloud Agent installation..."

# Download and install Qualys agent
cd /tmp
wget https://repo.qualys.com/centos/qualys-cloud-agent.x86_64.rpm
sudo rpm -ivh qualys-cloud-agent.x86_64.rpm

# Configure agent with activation code
sudo /opt/qualys/cloud-agent/bin/qualys-cloud-agent -a {activation_code}

# Start agent service
sudo systemctl enable qualys-cloud-agent
sudo systemctl start qualys-cloud-agent

echo "Qualys Cloud Agent installation completed"

# Verify installation
sudo /opt/qualys/cloud-agent/bin/qualys-cloud-agent -v
"""
        else:  # Windows
            script = f"""powershell -Command "
Write-Host 'Starting Qualys Cloud Agent installation...'

# Download Qualys agent installer
$DownloadUrl = 'https://repo.qualys.com/windows/qualyscloudagent.exe'
$InstallerPath = 'C:\\Temp\\qualyscloudagent.exe'

New-Item -ItemType Directory -Path 'C:\\Temp' -Force
Invoke-WebRequest -Uri $DownloadUrl -OutFile $InstallerPath

# Install Qualys agent
& $InstallerPath -a {activation_code}

# Start agent service
Start-Service -Name QualysAgent

Write-Host 'Qualys Cloud Agent installation completed'
"""
        
        logger.info(f"Generated Qualys installation script for {os_type}")
        return script

    def generate_health_check_script(self, os_type: str = "linux") -> str:
        """Generate Qualys agent health check script.
        
        Args:
            os_type: Operating system type
            
        Returns:
            Health check script content
        """
        if os_type.lower() == "linux":
            script = """#!/bin/bash
echo "Checking Qualys Cloud Agent status..."

# Check if agent is running
if systemctl is-active --quiet qualys-cloud-agent; then
    echo "Qualys Agent Status: RUNNING"
    exit 0
else
    echo "Qualys Agent Status: NOT RUNNING"
    systemctl start qualys-cloud-agent
    sleep 5
    exit 0
fi
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Checking Qualys Cloud Agent status...'
$Service = Get-Service -Name QualysAgent -ErrorAction SilentlyContinue
if ($Service -and $Service.Status -eq 'Running') {
    Write-Host 'Qualys Agent Status: RUNNING'
    exit 0
}
"""
        
        return script

    def generate_uninstall_script(self, os_type: str = "linux") -> str:
        """Generate Qualys agent uninstall script.
        
        Args:
            os_type: Operating system type
            
        Returns:
            Uninstall script content
        """
        if os_type.lower() == "linux":
            script = """#!/bin/bash
echo "Uninstalling Qualys Cloud Agent..."
sudo systemctl stop qualys-cloud-agent
sudo systemctl disable qualys-cloud-agent
sudo rpm -e qualys-cloud-agent
echo "Qualys Cloud Agent uninstalled successfully"
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Uninstalling Qualys Cloud Agent...'
Stop-Service -Name QualysAgent
Set-Service -Name QualysAgent -StartupType Disabled
"""
        
        return script
