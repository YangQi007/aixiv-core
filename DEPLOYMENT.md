# AIXIV Backend Deployment Guide

## Overview

This project uses a **two-phase deployment strategy**:

1. **Infrastructure Deployment** (Terraform) - One-time setup
2. **Application Deployment** (GitHub Actions) - Continuous deployment

## Phase 1: Infrastructure Setup (One-time)

### Prerequisites
- AWS CLI configured
- Terraform installed
- AWS credentials with appropriate permissions

### Steps

1. **Navigate to Terraform directory:**
   ```bash
   cd infrastructure/terraform
   ```

2. **Create terraform.tfvars with your values:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your actual values
   ```

3. **Initialize and apply Terraform:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Set up GitHub Secrets:**
   - Go to your GitHub repository → Settings → Secrets and variables → Actions
   - Add these secrets:
     - `AWS_ACCESS_KEY_ID`
     - `AWS_SECRET_ACCESS_KEY`

## Phase 2: Application Deployment (Automated)

### How it works

1. **Push to main branch** → Triggers GitHub Actions
2. **Test phase** → Runs unit tests
3. **Build phase** → Builds Docker image
4. **Deploy phase** → Updates ECS service

### GitHub Actions Workflow

The workflow (`.github/workflows/deploy.yml`) does:

1. **Test Job:**
   - Sets up Python 3.11
   - Installs dependencies
   - Runs pytest

2. **Build & Deploy Job:**
   - Configures AWS credentials
   - Logs into ECR
   - Builds and pushes Docker image
   - Updates ECS task definition
   - Deploys to ECS

## Security Best Practices

### ✅ What we're doing right:

1. **Secrets Management:**
   - AWS credentials stored in GitHub Secrets
   - No hardcoded secrets in code

2. **Infrastructure as Code:**
   - All AWS resources defined in Terraform
   - Version controlled infrastructure

3. **Container Security:**
   - Multi-stage Docker builds
   - Non-root user in container
   - Minimal base images

4. **Network Security:**
   - Private subnets for ECS tasks
   - Security groups with minimal access
   - ALB in public subnets only

### 🔧 Areas for improvement:

1. **Use AWS Secrets Manager** instead of environment variables
2. **Implement proper IAM roles** with least privilege
3. **Add container scanning** in CI/CD
4. **Set up monitoring and alerting**

## Environment Variables

### Required for Application:
- `DATABASE_URL` - PostgreSQL connection string
- `AWS_REGION` - AWS region
- `AWS_S3_BUCKET` - S3 bucket name
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `SECRET_KEY` - Application secret

## Monitoring

### CloudWatch Logs:
- Log group: `/ecs/aixiv-backend`
- Retention: 7 days

### Health Checks:
- Endpoint: `/api/health`
- Interval: 30 seconds
- Timeout: 5 seconds
- Retries: 3

## Troubleshooting

### Common Issues:

1. **ECS Task fails to start:**
   - Check CloudWatch logs
   - Verify environment variables
   - Check IAM permissions

2. **Database connection fails:**
   - Verify RDS endpoint
   - Check security groups
   - Confirm database credentials

3. **S3 upload fails:**
   - Check IAM permissions
   - Verify bucket name
   - Check AWS credentials

### Useful Commands:

```bash
# Check ECS service status
aws ecs describe-services --cluster aixiv-cluster --services aixiv-backend

# View CloudWatch logs
aws logs tail /ecs/aixiv-backend --follow

# Check ALB health
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

## Manual Database Migrations

After deployment, run migrations manually:

```bash
# Get task ARN
TASK_ARN=$(aws ecs list-tasks --cluster aixiv-cluster --service-name aixiv-backend --query 'taskArns[0]' --output text)

# Run migration task
aws ecs run-task \
  --cluster aixiv-cluster \
  --task-definition aixiv-backend \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-xxx],assignPublicIp=ENABLED}" \
  --overrides '{"containerOverrides":[{"name":"aixiv-backend","command":["alembic","upgrade","head"]}]}'
```

## Cost Optimization

### Current Resources:
- ECS Fargate: 2 tasks × 256 CPU units × 512 MB
- RDS Aurora: db.t3.medium
- ALB: Always on

### Optimization Tips:
1. **Scale down during off-hours** (use scheduled scaling)
2. **Use Spot instances** for non-critical workloads
3. **Implement auto-scaling** based on CPU/memory
4. **Monitor and optimize database queries**

## Next Steps

1. **Set up monitoring:**
   - CloudWatch dashboards
   - SNS notifications
   - Custom metrics

2. **Implement blue-green deployment:**
   - Zero-downtime deployments
   - Easy rollbacks

3. **Add security scanning:**
   - Container vulnerability scanning
   - Dependency scanning
   - SAST/DAST

4. **Set up staging environment:**
   - Separate infrastructure
   - Automated testing
   - Manual approval gates 