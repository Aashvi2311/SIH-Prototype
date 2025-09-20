#!/bin/bash

# Certificate Verification System MVP Startup Script
# Government of Jharkhand - Department of Higher and Technical Education

echo "🎓 Certificate Verification System MVP"
echo "========================================"
echo "Starting up..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if database exists
if [ ! -f "certificates.db" ]; then
    echo "📊 Setting up database with sample data..."
    python setup_sample_data.py
fi

# Start the application
echo "🚀 Starting application on http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py
