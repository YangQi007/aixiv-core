#!/bin/bash

# AIXIV Environment Setup Script

echo "🔧 AIXIV Environment Configuration"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
fi

echo ""
echo "Choose your environment:"
echo "1) Local Development (Docker Compose)"
echo "2) Production (AWS RDS)"
echo "3) View current configuration"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🏠 Setting up LOCAL DEVELOPMENT environment..."
        echo "This will use localhost:5432 for database"
        echo ""
        
        # Update .env for local development
        sed -i '' 's|DATABASE_URL=.*|DATABASE_URL=postgresql://aixiv_user:aixiv_password@localhost:5432/aixiv_db|' .env
        
        echo "✅ Local development environment configured!"
        echo "💡 Next steps:"
        echo "   1. Run: docker-compose up db"
        echo "   2. Run: ./start.sh"
        ;;
    2)
        echo ""
        echo "☁️  Setting up PRODUCTION environment..."
        echo "This will use AWS RDS for database"
        echo ""
        
        read -p "Enter your RDS endpoint: " rds_endpoint
        read -p "Enter your database username: " db_user
        read -p "Enter your database password: " db_pass
        read -p "Enter your database name: " db_name
        
        # Update .env for production
        sed -i '' "s|DATABASE_URL=.*|DATABASE_URL=postgresql://${db_user}:${db_pass}@${rds_endpoint}:5432/${db_name}|" .env
        
        echo "✅ Production environment configured!"
        echo "💡 Next steps:"
        echo "   1. Make sure your AWS credentials are set"
        echo "   2. Run: ./start.sh"
        ;;
    3)
        echo ""
        echo "📋 Current configuration:"
        echo "=========================="
        if [ -f .env ]; then
            echo "DATABASE_URL: $(grep '^DATABASE_URL=' .env | cut -d'=' -f2-)"
            echo "AWS_REGION: $(grep '^AWS_REGION=' .env | cut -d'=' -f2-)"
            echo "AWS_S3_BUCKET: $(grep '^AWS_S3_BUCKET=' .env | cut -d'=' -f2-)"
        else
            echo "❌ No .env file found"
        fi
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🔍 To view your full configuration, check the .env file"
echo "📚 For more help, see README.md or run ./start.sh" 