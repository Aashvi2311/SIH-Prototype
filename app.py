#!/usr/bin/env python3
"""
Fake Degree/Certificate Recognition System MVP
Government of Jharkhand - Department of Higher and Technical Education
"""

from flask import Flask
from app import create_app
import os

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
