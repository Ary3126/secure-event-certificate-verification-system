from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class Admin(db.Model):
    """Admin accounts (can create templates + generate certificates)."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    templates = db.relationship(
        'Template',
        backref='admin',
        lazy=True,
        cascade='all, delete-orphan',
    )
    certificates = db.relationship(
        'Certificate',
        backref='admin',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<Admin {self.username}>'


class Student(db.Model):
    """Student accounts (can download only certificates assigned to them)."""
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    certificates = db.relationship(
        'Certificate',
        backref='student',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<Student {self.username}>'


class Template(db.Model):
    """Certificate template model"""
    __tablename__ = 'templates'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    template_name = db.Column(db.String(120), nullable=False)
    background_path = db.Column(db.String(255), nullable=False)
    field_configuration = db.Column(db.JSON, nullable=False)  # Stores field positions and styles
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    certificates = db.relationship('Certificate', backref='template', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Template {self.template_name}>'


class Certificate(db.Model):
    """Certificate model"""
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('templates.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    certificate_uid = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True)
    recipient_name = db.Column(db.String(255), nullable=False)
    student_email = db.Column(db.String(120), nullable=False, index=True)
    course_name = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=True)
    pdf_path = db.Column(db.String(255), nullable=False)
    qr_code_path = db.Column(db.String(255), nullable=True)
    certificate_data = db.Column(db.JSON, nullable=False)  # Stores all dynamic field values
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    verification_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Certificate {self.certificate_uid}>'
    
    def increment_verification(self):
        """Increment verification count"""
        self.verification_count += 1
        db.session.commit()


class VerificationLog(db.Model):
    """Log of certificate verifications"""
    __tablename__ = 'verification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    certificate_id = db.Column(db.Integer, db.ForeignKey('certificates.id'), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    verified_at = db.Column(db.DateTime, default=datetime.utcnow)
    verification_method = db.Column(db.String(50), nullable=False)  # 'qr' or 'search'
    
    def __repr__(self):
        return f'<VerificationLog {self.id}>'
