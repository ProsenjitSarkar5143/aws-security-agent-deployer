"""Flask backend application for AWS Security Agent Deployer."""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
import os
from datetime import datetime
from typing import Dict, Any

from src.config import ConfigManager
from src.logger_config import LoggerManager, get_logger
from src.aws_handler import AWSHandler
from src.ssm_manager import SSMManager
from src.qualys_handler import QualysHandler
from src.crowdstrike_handler import CrowdStrikeHandler
from src.exceptions import DeployerException

# Initialize Flask app
app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

# Initialize logging
logger = get_logger('backend')

# Configuration
try:
    config_manager = ConfigManager()
except Exception as e:
    logger.error(f"Failed to load configuration: {e}")
    config_manager = None


# ==================== Helper Functions ====================

def get_response(success: bool, message: str, data: Any = None, status_code: int = 200) -> tuple:
    """Generate standard API response."""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data or {}
    }
    return jsonify(response), status_code


def handle_error(error: Exception, status_code: int = 500) -> tuple:
    """Handle exceptions and return error response."""
    logger.error(f"Error: {str(error)}", exc_info=True)
    return get_response(
        success=False,
        message=str(error),
        status_code=status_code
    )


# ==================== Health & Status Endpoints ====================

@app.route('/api/health', methods=['GET'])
def health_check() -> tuple:
    """Health check endpoint."""
    return get_response(
        success=True,
        message='Backend is healthy',
        data={'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}
    )


@app.route('/api/config', methods=['GET'])
def get_config() -> tuple:
    """Get current configuration."""
    try:
        if not config_manager:
            return handle_error('Configuration not loaded', 500)
        
        aws_cfg = config_manager.get_aws_config()
        deploy_cfg = config_manager.get_deployment_config()
        
        config_data = {
            'aws_region': aws_cfg.region,
            'deployment_mode': deploy_cfg.mode,
            'max_concurrent': deploy_cfg.parallel_instances
        }
        
        return get_response(
            success=True,
            message='Configuration retrieved',
            data=config_data
        )
    except Exception as e:
        return handle_error(e, 400)


# ==================== EC2 Instance Endpoints ====================

@app.route('/api/instances', methods=['GET'])
def list_instances() -> tuple:
    """List EC2 instances."""
    try:
        if not config_manager:
            return handle_error('Configuration not loaded', 500)
        
        aws_cfg = config_manager.get_aws_config()
        aws_handler = AWSHandler(aws_cfg)
        
        # Get query parameters
        state = request.args.get('state', 'running')
        region = request.args.get('region', aws_cfg.region)
        
        # Build filters
        filters = [{'Name': 'instance-state-name', 'Values': [state]}]
        
        instances = aws_handler.get_instances(filters=filters)
        
        # Format instances
        formatted_instances = []
        for inst in instances:
            formatted_instances.append({
                'instance_id': inst.get('InstanceId'),
                'instance_type': inst.get('InstanceType'),
                'state': inst.get('State', {}).get('Name'),
                'private_ip': inst.get('PrivateIpAddress'),
                'public_ip': inst.get('PublicIpAddress', 'N/A'),
                'tags': {tag['Key']: tag['Value'] for tag in inst.get('Tags', [])}
            })
        
        return get_response(
            success=True,
            message=f'Retrieved {len(formatted_instances)} instances',
            data={'instances': formatted_instances}
        )
    except Exception as e:
        return handle_error(e, 400)


@app.route('/api/instances/<instance_id>', methods=['GET'])
def get_instance_details(instance_id: str) -> tuple:
    """Get details for a specific instance."""
    try:
        if not config_manager:
            return handle_error('Configuration not loaded', 500)
        
        aws_cfg = config_manager.get_aws_config()
        aws_handler = AWSHandler(aws_cfg)
        
        instance = aws_handler.get_instance_by_id(instance_id)
        if not instance:
            return get_response(success=False, message='Instance not found', status_code=404)
        
        instance_data = {
            'instance_id': instance.get('InstanceId'),
            'instance_type': instance.get('InstanceType'),
            'state': instance.get('State', {}).get('Name'),
            'private_ip': instance.get('PrivateIpAddress'),
            'public_ip': instance.get('PublicIpAddress'),
            'launch_time': instance.get('LaunchTime').isoformat() if instance.get('LaunchTime') else None,
            'tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        }
        
        return get_response(
            success=True,
            message='Instance details retrieved',
            data=instance_data
        )
    except Exception as e:
        return handle_error(e, 400)


# ==================== Deployment Endpoints ====================

@app.route('/api/deploy', methods=['POST'])
def deploy_agent() -> tuple:
    """Deploy security agent to instances."""
    try:
        if not config_manager:
            return handle_error('Configuration not loaded', 500)
        
        data = request.get_json()
        agent_type = data.get('agent_type')
        instance_ids = data.get('instance_ids', [])
        deployment_mode = data.get('deployment_mode', 'lambda')
        dry_run = data.get('dry_run', False)
        
        if not agent_type or not instance_ids:
            return get_response(
                success=False,
                message='Missing required fields: agent_type, instance_ids',
                status_code=400
            )
        
        logger.info(f"Deployment requested: agent={agent_type}, instances={instance_ids}, mode={deployment_mode}")
        
        # Get handlers
        aws_cfg = config_manager.get_aws_config()
        deploy_cfg = config_manager.get_deployment_config()
        ssm_manager = SSMManager(aws_cfg, deploy_cfg)
        
        # Generate installation script
        if agent_type.lower() == 'qualys':
            qualys_cfg = config_manager.get_qualys_config()
            qualys_handler = QualysHandler(qualys_cfg)
            script = qualys_handler.generate_installation_script('ACTIVATION_CODE')
        elif agent_type.lower() == 'crowdstrike':
            cs_cfg = config_manager.get_crowdstrike_config()
            cs_handler = CrowdStrikeHandler(cs_cfg)
            script = cs_handler.generate_installation_script('CLIENT_ID', 'CLIENT_SECRET')
        else:
            return get_response(
                success=False,
                message=f'Unknown agent type: {agent_type}',
                status_code=400
            )
        
        if dry_run:
            return get_response(
                success=True,
                message='Dry-run successful',
                data={'script': script[:200] + '...', 'instances': len(instance_ids)}
            )
        
        # Execute deployment
        deployment_id = f"deploy_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        result = ssm_manager.execute_deployment_command(
            instance_ids=instance_ids,
            script=script,
            deployment_id=deployment_id
        )
        
        return get_response(
            success=True,
            message='Deployment completed',
            data=result
        )
    except Exception as e:
        return handle_error(e, 400)


@app.route('/api/deployments', methods=['GET'])
def get_deployments() -> tuple:
    """Get deployment history."""
    try:
        # This would fetch from a database in production
        deployments = [
            {
                'deployment_id': 'deploy_20260720_120000',
                'agent': 'qualys',
                'status': 'completed',
                'instances': 5,
                'successful': 4,
                'failed': 1,
                'timestamp': '2026-07-20T12:00:00Z'
            }
        ]
        
        return get_response(
            success=True,
            message='Deployments retrieved',
            data={'deployments': deployments}
        )
    except Exception as e:
        return handle_error(e, 400)


# ==================== Health Check Endpoints ====================

@app.route('/api/health-check', methods=['POST'])
def run_health_check() -> tuple:
    """Run health check on instances."""
    try:
        if not config_manager:
            return handle_error('Configuration not loaded', 500)
        
        data = request.get_json()
        agent_type = data.get('agent_type')
        instance_ids = data.get('instance_ids', [])
        
        if not agent_type or not instance_ids:
            return get_response(
                success=False,
                message='Missing required fields: agent_type, instance_ids',
                status_code=400
            )
        
        logger.info(f"Health check requested: agent={agent_type}, instances={instance_ids}")
        
        # Generate health check script
        if agent_type.lower() == 'qualys':
            qualys_cfg = config_manager.get_qualys_config()
            qualys_handler = QualysHandler(qualys_cfg)
            script = qualys_handler.generate_health_check_script()
        elif agent_type.lower() == 'crowdstrike':
            cs_cfg = config_manager.get_crowdstrike_config()
            cs_handler = CrowdStrikeHandler(cs_cfg)
            script = cs_handler.generate_health_check_script()
        else:
            return get_response(
                success=False,
                message=f'Unknown agent type: {agent_type}',
                status_code=400
            )
        
        # Execute health check
        aws_cfg = config_manager.get_aws_config()
        deploy_cfg = config_manager.get_deployment_config()
        ssm_manager = SSMManager(aws_cfg, deploy_cfg)
        
        results = ssm_manager.execute_health_check(instance_ids, script)
        
        return get_response(
            success=True,
            message='Health check completed',
            data=results
        )
    except Exception as e:
        return handle_error(e, 400)


# ==================== Frontend Routes ====================

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path: str):
    """Serve React frontend."""
    if path != '' and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return get_response(
        success=False,
        message='Endpoint not found',
        status_code=404
    )


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return get_response(
        success=False,
        message='Internal server error',
        status_code=500
    )


if __name__ == '__main__':
    logger.info("Starting Flask backend server")
    app.run(debug=True, host='0.0.0.0', port=5000)
