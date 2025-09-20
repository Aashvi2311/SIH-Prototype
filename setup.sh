#!/bin/bash

# Certificate Verification System MVP Setup Script
# Government of Jharkhand - Department of Higher and Technical Education

echo "🎓 Certificate Verification System MVP Setup"
echo "============================================="

# Check Python version
python_version=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then 
    echo "✓ Python $python_version detected"
else
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

# Check Tesseract installation
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract OCR found: $(tesseract --version | head -n1)"
else
    echo "❌ Tesseract OCR not found. Please install it first:"
    echo "   Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   macOS: brew install tesseract"
    echo "   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
fi

# Create virtual environment
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing it..."
    rm -rf venv
fi

echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Set up sample data
echo "📊 Setting up database with sample data..."
python setup_sample_data.py

# Make start script executable
chmod +x start.sh

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "To start the application:"
echo "  ./start.sh"
echo ""
echo "Or manually:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "The application will be available at http://localhost:5000"
