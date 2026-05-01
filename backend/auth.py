from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import re
from .models import Admin, Student, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to ensure the user is an admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    """Decorator to ensure the user is a student"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            flash('Student access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student').strip().lower()
        
        # Validation
        if not username or len(username) < 3:
            flash('Username must be at least 3 characters long', 'danger')
            return redirect(url_for('auth.register'))
        
        if not email or '@' not in email:
            flash('Invalid email address', 'danger')
            return redirect(url_for('auth.register'))

        if role not in ('admin', 'student'):
            flash('Invalid signup role', 'danger')
            return redirect(url_for('auth.register'))

        if role == 'admin':
            # Require Charusat email for admin signups
            if not re.match(r'^[^@\s]+@charusat\.edu\.in$', email, flags=re.IGNORECASE):
                flash('Admin signup requires a Charusat email like <id>@charusat.edu.in', 'danger')
                return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check if account exists (admin OR student)
        if Admin.query.filter_by(username=username).first() or Student.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))
        
        if Admin.query.filter_by(email=email).first() or Student.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        try:
            if role == 'admin':
                account = Admin(username=username, email=email)
            else:
                account = Student(username=username, email=email)

            account.set_password(password)
            db.session.add(account)
            db.session.commit()
            flash('Registration successful! Please log in', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET'])
def login():
    """Login selection page"""
    return render_template('login.html')


@auth_bp.route('/login/<role>', methods=['GET', 'POST'])
def login_role(role):
    """Login user with explicit role (admin or student)"""
    if role not in ('admin', 'student'):
        flash('Invalid login role', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if role == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:
            user = Student.query.filter_by(username=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account is disabled', 'danger')
                return redirect(url_for('auth.login_role', role=role))

            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = role
            session.permanent = True

            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()

            flash(f'Welcome back, {user.username}!', 'success')

            if role == 'admin':
                return redirect(url_for('main.dashboard'))
            else:
                return redirect(url_for('main.student_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login_role.html', role=role)

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_id = session.get('user_id')
    role = session.get('role')

    if role == 'admin':
        user = Admin.query.get(user_id)
    else:
        user = Student.query.get(user_id)

    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    return render_template('profile.html', user=user)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    user_id = session.get('user_id')
    role = session.get('role')

    if role == 'admin':
        user = Admin.query.get(user_id)
    else:
        user = Student.query.get(user_id)
    
    old_password = request.form.get('old_password', '')
    new_password = request.form.get('new_password', '')
    confirm_password = request.form.get('confirm_password', '')
    
    if not user.check_password(old_password):
        flash('Current password is incorrect', 'danger')
        return redirect(url_for('auth.profile'))
    
    if new_password != confirm_password:
        flash('New passwords do not match', 'danger')
        return redirect(url_for('auth.profile'))
    
    if len(new_password) < 6:
        flash('Password must be at least 6 characters long', 'danger')
        return redirect(url_for('auth.profile'))
    
    user.set_password(new_password)
    db.session.commit()
    flash('Password changed successfully', 'success')
    return redirect(url_for('auth.profile'))
