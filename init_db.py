#!/usr/bin/env python
"""
SGP - Certificate System Database Initialization Script
Run this script to initialize the database with sample data
"""

import os
import sys
from datetime import datetime

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

from backend.app import create_app
from backend.models import db, Admin, Template, Certificate

def init_db():
    """Initialize database with sample data"""
    app = create_app('development')
    
    with app.app_context():
        # Drop all tables and recreate
        print("Dropping existing database tables (if any)...")
        db.drop_all()
        print("Creating database tables...")
        db.create_all()
        
        # Create sample admin user
        print("Creating sample admin user...")
        admin = Admin(
            username='admin',
            email='admin@sgp.local',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        
        print("✓ Database initialized successfully!")
        print("\nSample Credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print("\nNote: Change password after first login!")

if __name__ == '__main__':
    init_db()
