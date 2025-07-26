variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "aws_access_key_id" {
  description = "AWS Access Key ID"
  type        = string
  sensitive   = true
}

variable "aws_secret_access_key" {
  description = "AWS Secret Access Key"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "Application secret key"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "Database username"
  type        = string
  default     = "aixiv_user"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "aixiv_db"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for file storage"
  type        = string
  default     = "aixiv-papers"
}

variable "s3_bucket_arn" {
  description = "S3 bucket ARN for file storage"
  type        = string
  default     = "arn:aws:s3:::aixiv-papers"
}

variable "task_cpu" {
  description = "CPU units for the ECS task"
  type        = number
  default     = 256
}

variable "task_memory" {
  description = "Memory for the ECS task (MiB)"
  type        = number
  default     = 512
}

variable "service_desired_count" {
  description = "Desired number of ECS service instances"
  type        = number
  default     = 2
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "aixiv"
    Environment = "production"
    ManagedBy   = "terraform"
  }
} 