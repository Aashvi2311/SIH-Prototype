# 🎓 Sattrix - Document Verification System
**By Team Oorja**

A comprehensive document verification system designed for educational institutions in Jharkhand. This MVP uses advanced OCR technology and fuzzy matching algorithms to verify the authenticity of educational documents.

![Sattrix Dashboard](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3+-lightgrey)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🔍 Document Verification**: Upload PDF/image documents for instant verification
- **🤖 OCR Processing**: Advanced text extraction using Tesseract OCR
- **🎯 Fuzzy Matching**: Intelligent matching against verified database records
- **📊 Admin Dashboard**: Real-time statistics and verification logs
- **🏛️ Institution Management**: Manage educational institutions and their certificates
- **🚨 Fraud Detection**: Automatic detection of suspicious activities and anomalies
- **📱 Responsive Design**: Works seamlessly on desktop and mobile devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR engine

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/sattrix-document-verification.git
   cd sattrix-document-verification
   ```

2. **Install Tesseract OCR:**
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Start the application:**
   ```bash
   ./start.sh
   ```

5. **Access the application:**
   Open your browser and navigate to `http://localhost:5000`

## 🖥️ Usage

### Document Verification
1. Go to the homepage
2. Drag & drop or select a document (PDF, JPG, PNG)
3. Click "Verify Document"
4. View detailed verification results

### Admin Features
- **Dashboard**: View verification statistics and recent activity
- **Manage Documents**: Add verified documents to the database
- **Manage Institutions**: Add and manage educational institutions
- **View Logs**: Monitor all verification attempts

## 🏗️ Architecture

```
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── routes.py            # Web routes and API endpoints
│   ├── ocr_utils.py         # OCR processing utilities
│   └── verification_engine.py # Core verification logic
├── templates/               # HTML templates
├── static/                 # Static assets (CSS, JS, images)
├── setup_sample_data.py    # Database initialization script
└── requirements.txt        # Python dependencies
```

## 🔧 Technology Stack

- **Backend**: Python, Flask, SQLAlchemy
- **Database**: SQLite (development), PostgreSQL (production)
- **OCR**: Tesseract, OpenCV, PIL
- **Frontend**: Bootstrap 5, JavaScript
- **Matching**: FuzzyWuzzy (Levenshtein distance)

## 📊 Sample Data

The system comes with pre-populated data from 5 Jharkhand institutions:
- Ranchi University
- Birla Institute of Technology (BIT Mesra)
- Central University of Jharkhand
- St. Xaviers College
- Government Polytechnic Ranchi

## 🔒 Security Features

- File type and size validation
- SQL injection protection
- XSS prevention
- Request logging and monitoring
- Suspicious activity detection

## 🌐 Deployment Options

### 1. **Heroku (Recommended for beginners)**
```bash
# Install Heroku CLI and login
heroku create your-app-name
git push heroku main
```

### 2. **Railway**
- Connect your GitHub repo to Railway
- Deploy with zero configuration

### 3. **Vercel/Netlify + Backend API**
- Deploy frontend to Vercel/Netlify
- Deploy API to Railway/Heroku

### 4. **VPS/Cloud Server**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 📝 Environment Variables

Create a `.env` file for production:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@host:port/dbname
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team Oorja

- **Project Lead**: [Your Name]
- **Development Team**: Team Oorja
- **Institution**: Government of Jharkhand - Department of Higher and Technical Education

## 🙏 Acknowledgments

- Government of Jharkhand for project support
- Educational institutions of Jharkhand for data collaboration
- Open source OCR and ML communities

---

**⭐ Star this repository if you find it helpful!**

For questions or support, please open an issue or contact Team Oorja.
