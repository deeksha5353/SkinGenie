from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import User, db

# Create a Blueprint for authentication features
# 'auth' is the name of this Blueprint
auth_bp = Blueprint('auth', __name__)

# Login route - handles both GET (show form) and POST (process form)
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is just viewing the page, show the login form
    if request.method == 'GET':
        return render_template('login.html')
    
    # If user submitted the form, process login
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Find user in database by email
        user = User.query.filter_by(email=email).first()
        
        # Check if user exists and password is correct
        if user and check_password_hash(user.password, password):
            # Store user ID in session to keep them logged in
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.view'))
        else:
            # Show error if login fails
            flash('Invalid email or password', 'error')
            return redirect(url_for('auth.login'))

# Signup route - handles both GET (show form) and POST (process form)
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    # If user is just viewing the page, show the signup form
    if request.method == 'GET':
        return render_template('register.html')
        
    # If user submitted the form, process registration
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('auth.signup'))
        
        # Check if email is already registered
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('auth.signup'))
        
        # Create new user with hashed password for security
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        
        try:
            # Save user to database
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('auth.login'))
        except:
            # Show error if registration fails
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('auth.signup'))

# Logout route - removes user from session
@auth_bp.route('/logout')
def logout():
    # Remove user_id from session
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login')) 