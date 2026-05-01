# Project Documentation

## Getting Started

This project is a web-based Digital Certificate Generation and Verification System built with Flask and SQLite.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python init_db.py
   ```

3. **Run Application**
   ```bash
   python backend/app.py
   ```

4. **Access Application**
   - Open browser and go to `http://localhost:5000`
   - Login with admin credentials (see init_db.py output)

## Project Components

### Backend (Flask)
- **config.py**: Configuration for different environments
- **models.py**: Database models (User, Template, Certificate, VerificationLog)
- **auth.py**: Authentication and user management
- **routes.py**: Main application routes
- **certificate_generator.py**: Certificate generation logic
- **verification.py**: Certificate verification routes
- **app.py**: Application entry point

### Frontend
- **templates/**: HTML templates for different pages
- **static/css/style.css**: Styling
- **static/js/script.js**: Client-side JavaScript

## Features Implemented

✓ User Authentication (Register/Login)
✓ Certificate Template Management
✓ Bulk Certificate Generation from CSV
✓ Unique Certificate IDs and QR Codes
✓ Public Certificate Verification
✓ User Dashboard and Statistics
✓ Verification Logs
✓ Responsive Design

## Workflow

1. **Admin creates account** → `/auth/register`
2. **Admin uploads certificate template** → `/template/manage`
3. **Admin uploads CSV with participant data** → `/certificates/generate`
4. **System generates certificates with unique IDs and QR codes**
5. **Public can verify certificates** → `/verify`
6. **Admin views statistics** → `/statistics`

## File Formats

### CSV Format (for certificate generation)
```
name,course,date
John Doe,Python,2024-02-21
```

### Template Requirements
- Format: PNG or JPG
- Recommended size: 1200x800px
- Contains certificate background design

## Security

- Password hashing with Werkzeug
- Session-based authentication
- Input validation on all forms
- SQL injection prevention via ORM
- XSS protection in templates

## Common Issues & Solutions

**Issue**: Port 5000 already in use
**Solution**: `python backend/app.py --port=5001`

**Issue**: Database errors
**Solution**: Delete `sgp.db` and run `python init_db.py` again

**Issue**: Missing modules
**Solution**: Run `pip install -r requirements.txt` again

## File Structure Summary

```
SGP/
├── backend/          # Flask application
├── frontend/         # HTML, CSS, JavaScript
├── certificates/     # Generated certificate storage
├── templates_upload/ # Uploaded template images
├── requirements.txt  # Dependencies
├── README.md         # Main documentation
├── init_db.py        # Database initialization
├── setup.bat/setup.sh # Setup scripts
└── sample_certificates.csv # Sample CSV
```

## Next Steps

1. Customize certificate templates for your organization
2. Test certificate generation with sample data
3. Configure email notifications (future enhancement)
4. Set up cloud storage integration (future enhancement)
5. Deploy to production server

---

For more detailed information, see README.md
