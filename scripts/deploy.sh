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
    
    # Get subnet and security group IDs (you'll need to update these)
    SUBNET_IDS="subnet-12345678,subnet-87654321"
    SECURITY_GROUP_IDS="sg-12345678"
    
    # Run migration task
    aws ecs run-task \
        --cluster $ECS_CLUSTER \
        --task-definition $ECS_TASK_DEFINITION \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_IDS],assignPublicIp=ENABLED}" \
        --overrides '{"containerOverrides":[{"name":"aixiv-backend","command":["alembic","upgrade","head"]}]}'
    
    log_info "Database migrations completed!"
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
    
    check_aws_cli
    check_docker
    check_environment
    
    build_and_push_image
    update_ecs_service
    wait_for_stability
    run_migrations
    get_service_url
    
    log_info "Deployment completed successfully!"
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