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

# Set variables
CLIENT_ID="{client_id}"
CLIENT_SECRET="{client_secret}"
API_ENDPOINT="https://api.crowdstrike.com"

# Get installation token from CrowdStrike API
echo "Retrieving installation credentials..."

TOKEN=$(curl -s -X POST "$API_ENDPOINT/oauth2/token" \
  -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&grant_type=client_credentials" \
  | jq -r '.access_token')

INSTALLATION_TOKEN=$(curl -s -X GET "$API_ENDPOINT/sensors/entities/download-installer/v1?os=Linux&os-version=x86_64" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.body[0].token')

# Download Falcon Sensor
echo "Downloading CrowdStrike Falcon Sensor..."
cd /tmp

wget "https://downloads.crowdstrike.com/releases/sensor/falcon-linux-sensor-latest-$INSTALLATION_TOKEN.tar.gz"
tar -xzf falcon-linux-sensor-latest-*.tar.gz

# Install Falcon Sensor
echo "Installing Falcon Sensor..."
cd falcon-sensor*
./install.sh

# Start Falcon Sensor
echo "Starting Falcon Sensor..."
sudo systemctl start falcon-sensor
sudo systemctl enable falcon-sensor

echo "CrowdStrike Falcon Sensor installation completed"

# Verify installation
sudo systemctl status falcon-sensor
"""
        else:  # Windows
            script = f"""powershell -Command "
$ClientID = '{client_id}'
$ClientSecret = '{client_secret}'
$ApiEndpoint = 'https://api.crowdstrike.com'

Write-Host 'Starting CrowdStrike Falcon Sensor installation...'

# Get installation token
Write-Host 'Retrieving installation credentials...'
$TokenBody = @{{
    'client_id' = $ClientID
    'client_secret' = $ClientSecret
    'grant_type' = 'client_credentials'
}}

$TokenResponse = Invoke-RestMethod -Uri "$ApiEndpoint/oauth2/token" `
    -Method Post `
    -Body $TokenBody

$Token = $TokenResponse.access_token

# Download Falcon Sensor
Write-Host 'Downloading CrowdStrike Falcon Sensor...'
$DownloadUrl = 'https://downloads.crowdstrike.com/releases/sensor/windows/x64/latest/falcon-windows-sensor-latest.exe'
$InstallerPath = 'C:\\Temp\\falcon-sensor.exe'

New-Item -ItemType Directory -Path 'C:\\Temp' -Force
Invoke-WebRequest -Uri $DownloadUrl -OutFile $InstallerPath

# Install Falcon Sensor
Write-Host 'Installing Falcon Sensor...'
& $InstallerPath /install /quiet /norestart

# Start Falcon Sensor service
Write-Host 'Starting Falcon Sensor service...'
Start-Service -Name CSFalconService

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

# Check if service is running
if systemctl is-active --quiet falcon-sensor; then
    echo "Falcon Sensor Status: RUNNING"
    
    # Get sensor details
    systemctl status falcon-sensor
    
    # Check connectivity
    sudo /opt/CrowdStrike/falcon-linux-sensor -p --verbose
    
    exit 0
else
    echo "Falcon Sensor Status: NOT RUNNING"
    systemctl start falcon-sensor
    sleep 5
    
    if systemctl is-active --quiet falcon-sensor; then
        echo "Sensor restarted successfully"
        exit 0
    else
        echo "Failed to restart sensor"
        exit 1
    fi
fi
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Checking CrowdStrike Falcon Sensor status...'

$Service = Get-Service -Name CSFalconService -ErrorAction SilentlyContinue

if ($Service) {
    if ($Service.Status -eq 'Running') {
        Write-Host 'Falcon Sensor Status: RUNNING'
        Get-Service -Name CSFalconService | Select-Object Status, StartType
        exit 0
    } else {
        Write-Host 'Falcon Sensor Status: STOPPED - Attempting restart'
        Start-Service -Name CSFalconService
        Start-Sleep -Seconds 5
        
        $Service = Get-Service -Name CSFalconService
        if ($Service.Status -eq 'Running') {
            Write-Host 'Sensor restarted successfully'
            exit 0
        } else {
            Write-Host 'Failed to restart sensor'
            exit 1
        }
    }
} else {
    Write-Host 'CrowdStrike Falcon Sensor not found'
    exit 1
}
"""
        
        return script

    @retry(max_attempts=3, delay=10)
    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        """Get CrowdStrike device status.
        
        Args:
            device_id: Device ID
            
        Returns:
            Device status dictionary
            
        Raises:
            CrowdStrikeException: If retrieval fails
        """
        try:
            if not self.access_token:
                raise CrowdStrikeException("Not authenticated with CrowdStrike API")
            
            url = f"{self.config.api_endpoint}/devices/entities/devices/v1"
            params = {"ids": [device_id]}
            
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=params,
                verify=True,
                timeout=self.config.timeout
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to get device status: {response.status_code}")
                return {"status": "unknown", "error": response.text}
            
            response_data = response.json()
            devices = response_data.get('resources', [])
            
            if devices:
                device = devices[0]
                status = {
                    "device_id": device_id,
                    "agent_version": device.get('agent_version', 'unknown'),
                    "last_seen": device.get('last_seen', 'never'),
                    "status": device.get('status', 'unknown'),
                    "os": device.get('os_version', 'unknown')
                }
            else:
                status = {"status": "not_found"}
            
            logger.info(f"Retrieved device status for {device_id}")
            return status
        
        except Exception as e:
            logger.error(f"Failed to get device status: {e}")
            raise CrowdStrikeException(f"Failed to get device status: {e}")

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
sudo systemctl stop falcon-sensor
sudo systemctl disable falcon-sensor
sudo /opt/CrowdStrike/falcon-linux-sensor --uninstall
echo "CrowdStrike Falcon Sensor uninstalled successfully"
"""
        else:  # Windows
            script = """powershell -Command "
Write-Host 'Uninstalling CrowdStrike Falcon Sensor...'
Stop-Service -Name CSFalconService
Set-Service -Name CSFalconService -StartupType Disabled
Uninstall-Package -Name 'CrowdStrike Falcon Sensor'
Write-Host 'CrowdStrike Falcon Sensor uninstalled successfully'
"""
        
        return script
