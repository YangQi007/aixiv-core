# AIXIV Backend Deployment Guide

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Terraform** installed (version >= 1.0)
4. **Docker** installed
5. **GitHub repository** with your code

## Step 1: Create S3 Bucket for Terraform State

```bash
# Create S3 bucket for Terraform state (replace with your bucket name)
aws s3 mb s3://aixiv-terraform-state --region us-east-1

# Enable versioning for state files
aws s3api put-bucket-versioning --bucket aixiv-terraform-state --versioning-configuration Status=Enabled
```

## Step 2: Create S3 Bucket for Papers

```bash
# Create S3 bucket for storing papers
aws s3 mb s3://aixiv-papers --region us-east-1

# Configure CORS for the S3 bucket
aws s3api put-bucket-cors --bucket aixiv-papers --cors-configuration '{
  "CORSRules": [
    {
      "AllowedHeaders": ["*"],
      "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
      "AllowedOrigins": ["https://aixiv.co", "http://localhost:3000"],
      "ExposeHeaders": ["ETag"]
    }
  ]
}'
```

## Step 3: Configure Terraform Variables

1. Copy the example variables file:
```bash
cp infrastructure/terraform/terraform.tfvars.example infrastructure/terraform/terraform.tfvars
```

2. Edit `infrastructure/terraform/terraform.tfvars` with your actual values:
```bash
# AWS Configuration
aws_region = "us-east-1"

# AWS Credentials (replace with your actual values)
aws_access_key_id     = "your_actual_aws_access_key_id"
aws_secret_access_key = "your_actual_aws_secret_access_key"

# Application Configuration
secret_key = "your_actual_secret_key_here_make_it_long_and_random"

# Database Configuration
db_username = "aixiv_user"
db_password = "your_secure_database_password"
db_name     = "aixiv_db"

# S3 Configuration
s3_bucket_name = "aixiv-papers"
s3_bucket_arn  = "arn:aws:s3:::aixiv-papers"
```

## Step 4: Deploy Infrastructure with Terraform

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the infrastructure
terraform apply
```

After successful deployment, note the outputs:
- ALB DNS name
- ECR repository URL
- RDS endpoint

## Step 5: Set up GitHub Secrets

In your GitHub repository, go to Settings > Secrets and variables > Actions, and add:

1. `AWS_ACCESS_KEY_ID` - Your AWS access key
2. `AWS_SECRET_ACCESS_KEY` - Your AWS secret key

## Step 6: Update Frontend Configuration

Update your frontend to use the new backend URL:

```javascript
// Replace localhost:8000 with your ALB DNS name
const API_BASE_URL = 'http://your-alb-dns-name.us-east-1.elb.amazonaws.com';

// Update your API calls
const response = await fetch(`${API_BASE_URL}/api/submit`, {
  // ... rest of your code
});
```

## Step 7: Deploy Application

### Option A: Using GitHub Actions (Recommended)
1. Push your code to the `main` branch
2. GitHub Actions will automatically build and deploy

### Option B: Manual Deployment
```bash
# Make the deployment script executable
chmod +x scripts/deploy.sh

# Deploy
./scripts/deploy.sh deploy
```

## Step 8: Set up Custom Domain (Optional)

1. **Create Route 53 hosted zone** for `aixiv.co`
2. **Request SSL certificate** in AWS Certificate Manager
3. **Update ALB listener** to use HTTPS
4. **Create Route 53 records** pointing to your ALB

## Step 9: Configure Environment Variables

Update your frontend environment variables:

```javascript
// .env.production
REACT_APP_API_URL=https://api.aixiv.co
REACT_APP_S3_BUCKET=aixiv-papers
```

## Step 10: Test the Deployment

1. **Health Check**: `curl https://api.aixiv.co/api/health`
2. **Upload URL**: Test file upload functionality
3. **Database**: Verify submissions are being stored
4. **S3**: Check files are being uploaded correctly

## Monitoring and Maintenance

### CloudWatch Logs
- Monitor application logs: `/ecs/aixiv-backend`
- Set up log retention policies

### Scaling
- Adjust `service_desired_count` in Terraform for scaling
- Set up auto-scaling policies if needed

### Security
- Regularly rotate AWS credentials
- Update dependencies
- Monitor security advisories

## Troubleshooting

### Common Issues

1. **ECS Service not starting**
   - Check CloudWatch logs
   - Verify environment variables
   - Check IAM permissions

2. **Database connection issues**
   - Verify RDS security groups
   - Check database credentials
   - Ensure VPC connectivity

3. **S3 upload failures**
   - Check IAM permissions
   - Verify CORS configuration
   - Check bucket policies

### Useful Commands

```bash
# Check ECS service status
aws ecs describe-services --cluster aixiv-cluster --services aixiv-backend

# View CloudWatch logs
aws logs tail /ecs/aixiv-backend --follow

# Check ALB health
aws elbv2 describe-target-health --target-group-arn your-target-group-arn

# Rollback deployment
./scripts/deploy.sh rollback
```

## Cost Optimization

1. **Use Spot instances** for non-critical workloads
2. **Set up auto-scaling** based on demand
3. **Monitor resource usage** with CloudWatch
4. **Use reserved instances** for predictable workloads

## Security Best Practices

1. **Use IAM roles** instead of access keys where possible
2. **Enable VPC Flow Logs** for network monitoring
3. **Use AWS Secrets Manager** for sensitive data
4. **Regularly update** dependencies and base images
5. **Enable CloudTrail** for audit logging 