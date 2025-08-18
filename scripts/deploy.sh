#!/bin/bash

# AIXIV Backend Deployment Script
# This script deploys the FastAPI application to AWS ECS Fargate

set -e

# Configuration
AWS_REGION=${AWS_REGION:-"us-east-1"}
ECR_REPOSITORY="aixiv-backend"
ECS_CLUSTER="aixiv-cluster"
ECS_SERVICE="aixiv-backend"
ECS_TASK_DEFINITION="aixiv-backend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
        exit 1
    fi
}

# Check if required environment variables are set
check_environment() {
    if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
        log_error "AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
        exit 1
    fi
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building Docker image..."
    
    # Get ECR login token
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Build image
    docker build -f Dockerfile.prod -t $ECR_REPOSITORY:latest .
    
    # Tag image
    ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
    docker tag $ECR_REPOSITORY:latest $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    # Push image
    log_info "Pushing image to ECR..."
    docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    log_info "Image pushed successfully!"
}

# Update ECS service
update_ecs_service() {
    log_info "Updating ECS service..."
    
    # Get current task definition
    aws ecs describe-task-definition --task-definition $ECS_TASK_DEFINITION --query taskDefinition > task-definition.json
    
    # Update image in task definition
    ECR_REGISTRY=$(aws sts get-caller-identity --query Account --output text).dkr.ecr.$AWS_REGION.amazonaws.com
    sed -i "s|$ECR_REGISTRY/$ECR_REPOSITORY:[^\"']*|$ECR_REGISTRY/$ECR_REPOSITORY:latest|g" task-definition.json
    
    # Register new task definition
    NEW_TASK_DEF_ARN=$(aws ecs register-task-definition --cli-input-json file://task-definition.json --query taskDefinition.taskDefinitionArn --output text)
    
    # Update service
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --task-definition $NEW_TASK_DEF_ARN
    
    log_info "ECS service updated successfully!"
}

# Wait for service stability
wait_for_stability() {
    log_info "Waiting for service to become stable..."
    aws ecs wait services-stable --cluster $ECS_CLUSTER --services $ECS_SERVICE
    log_info "Service is now stable!"
}

# Run database migrations
run_migrations() {
    log_info "Running database migrations..."
    
    # Get subnet and security group IDs dynamically from infrastructure
    log_info "Getting network configuration from infrastructure..."
    
    # Try to get subnet IDs from VPC
    SUBNET_IDS=$(aws ec2 describe-subnets \
        --filters "Name=tag:Name,Values=*private*" \
        --query 'Subnets[*].SubnetId' \
        --output text | tr '\t' ',')
    
    # Try to get security group IDs
    SECURITY_GROUP_IDS=$(aws ec2 describe-security-groups \
        --filters "Name=group-name,Values=*aixiv*" \
        --query 'SecurityGroups[*].GroupId' \
        --output text | tr '\t' ',')
    
    if [ -z "$SUBNET_IDS" ] || [ -z "$SECURITY_GROUP_IDS" ]; then
        log_warn "Could not determine network configuration automatically."
        log_warn "Skipping database migrations. Run them manually if needed."
        log_warn "You can run migrations manually with:"
        log_warn "  docker compose exec api alembic upgrade head"
        return 0
    fi
    
    log_info "Using subnets: $SUBNET_IDS"
    log_info "Using security groups: $SECURITY_GROUP_IDS"
    
    # Run migration task
    log_info "Starting migration task..."
    aws ecs run-task \
        --cluster $ECS_CLUSTER \
        --task-definition $ECS_TASK_DEFINITION \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_IDS],assignPublicIp=ENABLED}" \
        --overrides '{"containerOverrides":[{"name":"aixiv-backend","command":["alembic","upgrade","head"]}]}' \
        --query 'tasks[0].taskArn' \
        --output text > /tmp/migration-task-arn.txt
    
    if [ $? -eq 0 ]; then
        MIGRATION_TASK_ARN=$(cat /tmp/migration-task-arn.txt)
        log_info "Migration task started: $MIGRATION_TASK_ARN"
        log_info "Database migrations completed!"
    else
        log_warn "Failed to start migration task. Run migrations manually if needed."
    fi
    
    # Cleanup
    rm -f /tmp/migration-task-arn.txt
}

# Get service URL
get_service_url() {
    log_info "Getting service URL..."
    ALB_DNS=$(aws elbv2 describe-load-balancers --query 'LoadBalancers[?contains(LoadBalancerName, `aixiv`)].DNSName' --output text)
    if [ ! -z "$ALB_DNS" ]; then
        log_info "Service URL: http://$ALB_DNS"
    else
        log_warn "Could not determine service URL. Check the ALB manually."
    fi
}

# Main deployment function
deploy() {
    log_info "Starting deployment..."
    
    # Check prerequisites
    check_aws_cli
    check_docker
    check_environment
    
    # Build and push image
    log_info "Step 1/5: Building and pushing Docker image..."
    if ! build_and_push_image; then
        log_error "Failed to build and push image. Aborting deployment."
        exit 1
    fi
    
    # Update ECS service
    log_info "Step 2/5: Updating ECS service..."
    if ! update_ecs_service; then
        log_error "Failed to update ECS service. Aborting deployment."
        exit 1
    fi
    
    # Wait for stability
    log_info "Step 3/5: Waiting for service stability..."
    if ! wait_for_stability; then
        log_error "Service failed to stabilize. Consider rolling back."
        exit 1
    fi
    
    # Run migrations (optional - won't fail deployment)
    log_info "Step 4/5: Running database migrations..."
    run_migrations
    
    # Get service URL
    log_info "Step 5/5: Getting service information..."
    get_service_url
    
    log_info "🎉 Deployment completed successfully!"
    log_info "Your application is now live!"
}

# Rollback function
rollback() {
    log_warn "Rolling back deployment..."
    
    # Get previous task definition
    PREVIOUS_TASK_DEF=$(aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --query 'services[0].taskDefinition' --output text)
    
    # Update service to previous task definition
    aws ecs update-service --cluster $ECS_CLUSTER --service $ECS_SERVICE --task-definition $PREVIOUS_TASK_DEF
    
    wait_for_stability
    
    log_info "Rollback completed!"
}

# Show usage
usage() {
    echo "Usage: $0 [deploy|rollback]"
    echo "  deploy   - Deploy the application to ECS"
    echo "  rollback - Rollback to previous deployment"
    exit 1
}

# Main script
case "${1:-}" in
    deploy)
        deploy
        ;;
    rollback)
        rollback
        ;;
    *)
        usage
        ;;
esac 