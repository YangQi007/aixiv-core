#!/bin/bash

# AIXIV Backend Startup Script

echo "🚀 Starting AIXIV Backend API..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration before running again."
    echo "   Required: DATABASE_URL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY"
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
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    engine.connect()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
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
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 