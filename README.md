# AWS Security Agent Deployer

A comprehensive GitHub-integrated application for remotely deploying security agents (Qualys or CrowdStrike) on AWS EC2 instances using both serverless (Lambda) and on-demand (EC2) deployment options.

## 🌟 Features

- **Dual Deployment Options**
  - Lambda-based: Serverless, cost-effective, auto-scaling
  - EC2-based: Full control, custom configurations, persistent
- **GitHub Integration**: Trigger deployments via GitHub Actions workflows
- **AWS EC2 Management**: Discover, filter, and manage EC2 instances
- **Multi-Agent Support**: Qualys Cloud Agent & CrowdStrike Falcon Agent
- **AWS Systems Manager**: Execute commands on instances remotely
- **Status Monitoring**: Real-time deployment tracking and health checks
- **Comprehensive Logging**: CloudWatch, GitHub Actions, and local logs
- **Infrastructure as Code**: Terraform for complete environment setup
- **Security First**: IAM role-based access, encrypted credentials, audit trails
- **Error Handling**: Automatic retries, rollback capability, detailed error reporting

## 📊 Architecture

### Lambda-Based Deployment
```
GitHub Actions (webhook)
        ↓
   API Gateway
        ↓
   Lambda Function
        ↓
AWS Systems Manager Session Manager
        ↓
EC2 Instances → Qualys/CrowdStrike Agents
```

### EC2-Based Deployment
```
GitHub Actions (webhook)
        ↓
   EC2 Deployer Instance
        ↓
AWS Systems Manager Run Command
        ↓
Target EC2 Instances → Qualys/CrowdStrike Agents
```

## 🔧 Prerequisites

- **AWS Account** with EC2, Lambda, IAM permissions
- **GitHub Account** with repository access
- **Qualys API Credentials** (API URL, username, password)
- **CrowdStrike API Credentials** (Client ID, Client Secret)
- **AWS CLI** v2 installed locally
- **Terraform** v1.0+ installed
- **Python** 3.9+ installed

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/ProsenjitSarkar5143/aws-security-agent-deployer.git
cd aws-security-agent-deployer
```

### 2. Configure GitHub Secrets

Add the following secrets to your GitHub repository (Settings → Secrets):

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (e.g., us-east-1)
QUALYS_API_URL
QUALYS_USERNAME
QUALYS_PASSWORD
CROWDSTRIKE_CLIENT_ID
CROWDSTRIKE_CLIENT_SECRET
DEPLOYMENT_MODE (lambda or ec2)
SLACK_WEBHOOK_URL (optional)
```

### 3. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region
# Enter default output format
```

### 4. Deploy Infrastructure

#### For Lambda-Based Deployment:
```bash
cd terraform/lambda
terraform init
terraform plan -var="deployment_mode=lambda"
terraform apply -var="deployment_mode=lambda"
```

#### For EC2-Based Deployment:
```bash
cd terraform/ec2
terraform init
terraform plan -var="deployment_mode=ec2"
terraform apply -var="deployment_mode=ec2"
```

### 5. Create Configuration File
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your specific settings
```

### 6. Install Dependencies
```bash
pip install -r requirements.txt
```

## 📁 Directory Structure

```
aws-security-agent-deployer/
├── src/
│   ├── __init__.py
│   ├── deploy_agent.py                  # Main CLI entry point
│   ├── aws_handler.py                   # EC2 instance management
│   ├── qualys_handler.py                # Qualys agent deployment
│   ├── crowdstrike_handler.py           # CrowdStrike agent deployment
│   ├── ssm_manager.py                   # AWS Systems Manager integration
│   ├── logger_config.py                 # Logging setup
│   ├── config.py                        # Configuration loader
│   ├── utils.py                         # Utility functions
│   └── exceptions.py                    # Custom exceptions
│
├── lambda/
│   ├── lambda_handler.py                # Lambda entry point
│   ├── lambda_qualys.py                 # Qualys Lambda handler
│   ├── lambda_crowdstrike.py            # CrowdStrike Lambda handler
│   └── requirements.txt                 # Lambda dependencies
│
├── .github/
│   └── workflows/
│       ├── deploy-qualys.yml            # Qualys deployment workflow
│       ├── deploy-crowdstrike.yml       # CrowdStrike deployment workflow
│       ├── health-check.yml             # Health check workflow
│       ├── rollback.yml                 # Rollback workflow
│       └── test.yml                     # Unit tests
│
├── terraform/
│   ├── lambda/
│   │   ├── main.tf                      # Lambda infrastructure
│   │   ├── variables.tf                 # Variables
│   │   ├── outputs.tf                   # Outputs
│   │   ├── iam.tf                       # IAM roles
│   │   ├── api_gateway.tf               # API Gateway setup
│   │   ├── cloudwatch.tf                # CloudWatch logs
│   │   └── lambda.tf                    # Lambda function
│   │
│   └── ec2/
│       ├── main.tf                      # EC2 infrastructure
│       ├── variables.tf                 # Variables
│       ├── outputs.tf                   # Outputs
│       ├── iam.tf                       # IAM roles
│       ├── security_groups.tf           # Security groups
│       ├── ec2.tf                       # EC2 instance
│       ├── user_data.sh                 # EC2 user data script
│       └── cloudwatch.tf                # CloudWatch setup
│
├── scripts/
│   ├── install-qualys.sh                # Qualys installation script
│   ├── install-crowdstrike.sh           # CrowdStrike installation script
│   ├── health-check.sh                  # Agent health verification
│   ├── uninstall-agent.sh               # Agent removal script
│   └── pre-deployment-check.sh          # Environment validation
│
├── tests/
│   ├── __init__.py
│   ├── test_aws_handler.py              # AWS handler tests
│   ├── test_qualys_handler.py           # Qualys handler tests
│   ├── test_crowdstrike_handler.py      # CrowdStrike handler tests
│   ├── test_ssm_manager.py              # SSM manager tests
│   └── conftest.py                      # Pytest configuration
│
├── config.example.yaml                  # Example configuration
├── requirements.txt                     # Python dependencies
├── docker-compose.yml                   # Local development
├── Dockerfile                           # Container image
├── .gitignore                           # Git ignore rules
├── DEPLOYMENT_GUIDE.md                  # Detailed guide
├── ARCHITECTURE.md                      # Architecture details
├── TROUBLESHOOTING.md                   # Troubleshooting guide
├── LICENSE                              # MIT License
└── .env.example                         # Environment variables template
```

## 💻 Usage

### Command Line Interface

#### Deploy Qualys Agent
```bash
python3 src/deploy_agent.py deploy \
  --agent qualys \
  --instances i-123456 i-789012 \
  --region us-east-1 \
  --deployment-mode lambda \
  --dry-run false
```

#### Deploy CrowdStrike Agent
```bash
python3 src/deploy_agent.py deploy \
  --agent crowdstrike \
  --instances i-123456 i-789012 \
  --region us-east-1 \
  --deployment-mode ec2 \
  --dry-run false
```

#### Auto-Discover Instances by Tag
```bash
python3 src/deploy_agent.py deploy \
  --agent qualys \
  --tag Environment:production \
  --region us-east-1 \
  --deployment-mode lambda
```

#### Check Deployment Status
```bash
python3 src/deploy_agent.py status \
  --agent qualys \
  --instance i-123456 \
  --region us-east-1
```

#### List All Instances
```bash
python3 src/deploy_agent.py list-instances \
  --region us-east-1 \
  --filter running
```

## 🔐 Security Considerations

### Best Practices

1. **Credential Management**
   - Store all credentials in GitHub Secrets (never in code)
   - Rotate credentials every 90 days
   - Use AWS Secrets Manager for sensitive data

2. **IAM Permissions**
   - Follow principle of least privilege
   - Use separate IAM users for Lambda and EC2 deployments
   - Regularly audit IAM policies

3. **Encryption**
   - Enable SSL/TLS for all API communications
   - Use KMS for data encryption at rest
   - Enable CloudTrail for audit logging

## 📈 Deployment Scenarios

### Deploy to Production
```bash
python3 src/deploy_agent.py deploy \
  --agent qualys \
  --tag Environment:production \
  --deployment-mode lambda \
  --parallel 5
```

## 📚 Additional Resources

- [Detailed Deployment Guide](DEPLOYMENT_GUIDE.md)
- [Architecture Documentation](ARCHITECTURE.md)
- [Troubleshooting Guide](TROUBLESHOOTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 👤 Author

**Prosenjit Sarkar**
- GitHub: [@ProsenjitSarkar5143](https://github.com/ProsenjitSarkar5143)

---

**Version**: 1.0.0
