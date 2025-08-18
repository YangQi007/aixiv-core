#!/bin/bash

# ⚠️  ⚠️  ⚠️  WARNING: NOT FOR NEW DEVELOPERS ⚠️  ⚠️  ⚠️
# 
# This script is for ADVANCED USERS ONLY.
# 
# 🚨 NEW DEVELOPERS: Use 'docker compose up' instead!
# 🚨 This script is only for troubleshooting when Docker breaks.
# 🚨 If you're new here, STOP and ask for help.
# 
# AIXIV Backend Startup Script (Backup/Alternative to Docker Compose)
# 
# ⚠️  PRIMARY DEVELOPMENT METHOD: Use 'docker compose up'
# 📋  This script is a backup option for:
#     - Docker troubleshooting (advanced users only)
#     - Performance debugging (advanced users only)
#     - Native Python development (advanced users only)
#     - CI/CD scenarios (advanced users only)

echo "🚨 ADVANCED USERS ONLY - NOT FOR NEW DEVELOPERS 🚨"
echo "🚀 Starting AIXIV Backend API (Native Python Mode)..."
echo "⚠️  WARNING: This script starts the API outside of Docker."
echo "   If you're using 'docker compose up', STOP IT FIRST to avoid conflicts!"
echo ""
echo "💡 RECOMMENDED: Use 'docker compose up' instead (simpler, more consistent)"
echo "💡 This script is a backup option for special cases only."
echo "🚨 If you're new here, STOP and use 'docker compose up' instead!"
echo ""

# Check if Docker Compose is running
if docker compose ps | grep -q "api"; then
    echo "❌ Docker Compose API is already running!"
    echo "💡 Stop it first with: docker compose down"
    echo "💡 Or use Docker Compose instead: docker compose up"
    echo ""
    echo "🎯 RECOMMENDATION: Use Docker Compose for normal development"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    echo "   Required: DATABASE_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
    echo ""
    echo "💡 For local development: Use DATABASE_URL with localhost"
    echo "💡 For production: Use DATABASE_URL with your RDS endpoint"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if database is accessible
echo "🔍 Checking database connection..."
python -c "
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('❌ DATABASE_URL not found in .env file')
    exit(1)

try:
    engine = create_engine(db_url)
    engine.connect()
    print('✅ Database connection successful')
    print(f'📍 Connected to: {db_url.split(\"@\")[1] if \"@\" in db_url else \"Unknown\"}')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    print('💡 Make sure your database is running and accessible')
    print('💡 For local development: Run docker-compose up db')
    print('💡 For production: Check your RDS endpoint and credentials')
    exit(1)
"

# Run database migrations
echo "🗄️  Running database migrations..."
alembic upgrade head

# Start the server
echo "🌐 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Health check: http://localhost:8000/api/health"
echo ""
echo "💡 This is NATIVE Python mode (not Docker)"
echo "💡 For Docker mode, use: docker compose up"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 