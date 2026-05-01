py# SGP: Digital Certificate Generation & Verification System

A web-based application for automated certificate generation, management, and verification using unique IDs and QR codes.

## 📋 Project Features

- **Admin Authentication**: Secure login and registration for administrators
- **Certificate Templates**: Upload custom background images for certificate design
- **Bulk Generation**: Generate certificates in bulk using CSV files
- **Unique IDs & QR Codes**: Each certificate gets a unique identifier and QR code
- **Public Verification**: Verify certificates using ID search or QR code scanning
- **Statistics Dashboard**: Track certificate metrics and verification statistics
- **User Management**: Manage user profiles and passwords

## 🏗️ Project Structure

```
SGP/
├── backend/
│   ├── app.py                      # Flask application entry point
│   ├── config.py                   # Configuration settings
│   ├── models.py                   # Database models
│   ├── auth.py                     # Authentication routes
│   ├── routes.py                   # Main application routes
│   ├── certificate_generator.py    # Certificate generation logic
│   └── verification.py             # Certificate verification routes
├── frontend/
│   ├── templates/
│   │   ├── base.html               # Base template
│   │   ├── index.html              # Home page
│   │   ├── login.html              # Login page
│   │   ├── register.html           # Registration page
│   │   ├── dashboard.html          # Admin dashboard
│   │   ├── template_manager.html   # Template management
│   │   ├── generator.html          # Certificate generator
│   │   ├── certificates_list.html  # Certificates listing
│   │   ├── verify.html             # Public verification page
│   │   ├── profile.html            # User profile
│   │   ├── statistics.html         # Statistics page
│   │   ├── certificate_details.html # Certificate details
│   │   ├── 404.html                # 404 error page
│   │   └── 500.html                # 500 error page
│   └── static/
│       ├── css/
│       │   └── style.css           # Main stylesheet
│       └── js/
│           └── script.js           # Main JavaScript
├── certificates/                   # Generated certificates storage
├── templates_upload/               # Uploaded templates storage
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
└── README.md                       # This file
```

## 🛠️ Technologies Used

### Frontend
- HTML5
- CSS3
- JavaScript (Vanilla)

### Backend
- Python 3.8+
- Flask 2.3.3
- SQLAlchemy 2.0.20

### Database
- SQLite

### Libraries
- **qrcode**: QR code generation
- **Pillow**: Image processing
- **pandas**: CSV processing
- **reportlab**: PDF generation
- **python-dotenv**: Environment variables

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Steps

1. **Clone or download the project**
   ```bash
   cd d:\SEMESTER-4\SGP
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file** (optional)
   ```bash
   cp .env.example .env
   ```

5. **Initialize the database**
   ```bash
   python -c "from backend.app import create_app; app = create_app(); app.app_context().push()"
   ```

## 🚀 Running the Application

```bash
python backend/app.py
```

The application will be available at `http://localhost:5000`

### Development Server
```bash
FLASK_ENV=development python backend/app.py
```

## 📝 Usage Guide

### For Administrators

1. **Register/Login**
   - Create an account or login at `/auth/login`
   - Your dashboard is available at `/dashboard`

2. **Create Certificate Templates**
   - Go to "Templates" section
   - Upload a certificate background image (PNG or JPG)
   - Define template name and field configuration
   - Click "Upload Template"

3. **Generate Certificates**
   - Go to "Generate" section
   - Select a template
   - Upload a CSV file with participant data (name, course)
   - Click "Generate Certificates"
   - Certificates will be generated with unique IDs and QR codes

4. **Manage Certificates**
   - View all generated certificates in "Certificates" section
   - Download certificates individually
   - View verification statistics

### For Public Users

1. **Verify Certificates**
   - Go to the public "Verify" page
   - Enter certificate ID or scan QR code
   - View certificate details and authenticity status

## 📊 Database Schema

### Users Table
- `id`: Integer (Primary Key)
- `username`: String (Unique)
- `email`: String (Unique)
- `password_hash`: String
- `created_at`: DateTime
- `last_login`: DateTime
- `is_active`: Boolean

### Templates Table
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `template_name`: String
- `background_path`: String
- `field_configuration`: JSON
- `created_at`: DateTime
- `updated_at`: DateTime
- `is_active`: Boolean

### Certificates Table
- `id`: Integer (Primary Key)
- `user_id`: Integer (Foreign Key)
- `template_id`: Integer (Foreign Key)
- `certificate_uid`: String (Unique)
- `recipient_name`: String
- `course_name`: String
- `issue_date`: DateTime
- `expiry_date`: DateTime (Optional)
- `pdf_path`: String
- `qr_code_path`: String
- `certificate_data`: JSON
- `created_at`: DateTime
- `verification_count`: Integer

### Verification Logs Table
- `id`: Integer (Primary Key)
- `certificate_id`: Integer (Foreign Key)
- `ip_address`: String
- `user_agent`: String
- `verified_at`: DateTime
- `verification_method`: String ("qr" or "search")

## 🔒 Security Features

- Password hashing using Werkzeug security
- Session-based authentication
- CSRF protection ready
- Secure file upload validation
- SQL injection prevention via SQLAlchemy ORM
- XSS protection in templates

## 📋 CSV Format for Certificate Generation

Your CSV file should contain at least these columns:

```csv
name,course,date (optional)
John Doe,Python Basics,2024-02-21
Jane Smith,Web Development,2024-02-21
```

Required columns:
- `name`: Recipient's name
- `course`: Course or certificate name

Optional columns:
- `date`: Issue date (format: YYYY-MM-DD)

## 🎨 Certificate Customization

1. Upload certificate background image (recommended size: 1200x800px)
2. Define custom fields in template configuration
3. System automatically adds:
   - Recipient name
   - Course name
   - Issue date
   - Unique certificate ID
   - QR code in corner

## 🐛 Troubleshooting

### Issue: Database locked
**Solution**: Delete `sgp.db` file and restart the application

### Issue: QR codes not generating
**Solution**: Ensure `qrcode` and `Pillow` libraries are installed

### Issue: Certificate images not displaying
**Solution**: Check if template images exist in `templates_upload/` folder and paths are correct

### Issue: Import errors
**Solution**: Make sure all requirements are installed: `pip install -r requirements.txt`

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/logout` - Logout user
- `GET /auth/profile` - View user profile
- `POST /auth/change-password` - Change password

### Templates
- `GET /template/manage` - List templates
- `POST /template/upload` - Upload new template
- `POST /template/delete/<id>` - Delete template

### Certificates
- `GET /certificates/generate` - Certificate generation page
- `POST /certificates/generate` - Generate certificates from CSV
- `GET /certificates/list` - List user's certificates
- `GET /certificates/download/<id>` - Download certificate

### Verification
- `GET /verify/` - Public verification page
- `POST /verify/search` - Search certificate by ID
- `GET /verify/qr/<uid>` - Verify by QR code
- `GET /verify/api/certificate/<uid>` - Get certificate details (API)

## 🔮 Future Enhancements

- Multi-organization support
- Email certificate delivery
- Cloud storage integration (AWS S3, Google Cloud)
- Blockchain verification
- Mobile-responsive UI improvements
- Payment gateway integration
- Batch verification
- Certificate templates marketplace
- API authentication (JWT)
- Advanced analytics and reporting

## 📞 Support

For issues or questions, please refer to the project documentation or contact the development team.

## 📄 License

This project is provided for educational purposes.

---

**Last Updated**: February 21, 2024
**Version**: 1.0.0
