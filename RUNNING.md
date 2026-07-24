# Running the Application

## Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Backend Setup

```bash
# Install Python dependencies
pip install -r requirements-backend.txt
pip install -r requirements.txt

# Create config file
cp config.example.yaml config.yaml
# Edit config.yaml with your settings

# Run Flask backend
python app.py
```

## Docker Setup (Optional)

```bash
# Build and run with Docker
docker-compose up -d
```

## Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health

## Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - AWS_REGION=us-east-1
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

## Configuration

Update `config.yaml` with:
- AWS region and credentials
- Qualys API URL and credentials
- CrowdStrike API endpoint and credentials
- Deployment mode (lambda or ec2)

## Environment Variables

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export QUALYS_API_URL=https://qualysapi.example.com
export QUALYS_USERNAME=your_username
export QUALYS_PASSWORD=your_password
export CROWDSTRIKE_CLIENT_ID=your_client_id
export CROWDSTRIKE_CLIENT_SECRET=your_client_secret
```

## Production Deployment

### AWS Elastic Beanstalk

```bash
eb init -p python-3.9 aws-security-agent-deployer
eb create prod-env
eb deploy
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
kubectl expose deployment security-deployer --type=LoadBalancer
```

## Troubleshooting

### Backend won't start
- Check AWS credentials are configured
- Verify config.yaml exists and is valid
- Check Flask logs for errors

### Frontend can't connect to backend
- Ensure backend is running on port 5000
- Check CORS configuration in app.py
- Verify API endpoints in fetch calls

### Instances not showing
- Verify AWS credentials have EC2 read permissions
- Check AWS region in config matches instances
- Review security group and VPC settings
