from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production

# Mock user database (replace with real database in production)
users = {
    'demo@example.com': {'password': 'demo123'}
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email in users and users[email]['password'] == password:
            session['user'] = email
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        fullname = request.form.get('fullname')
        
        # Basic validation
        if not email or not password or not confirm_password or not fullname:
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        if email in users:
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        # Add new user (in a real app, you'd hash the password)
        users[email] = {
            'password': password,
            'fullname': fullname
        }
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    # Mock recommendations (replace with real recommendation logic)
    recommendations = [
        {
            'name': 'Perfect Match Foundation',
            'description': 'Lightweight, buildable coverage perfect for your skin type',
            'price': '35.99'
        },
        {
            'name': 'Hydrating Concealer',
            'description': 'Creamy concealer that brightens and hydrates',
            'price': '24.99'
        },
        {
            'name': 'Natural Finish Powder',
            'description': 'Sets makeup while maintaining a natural glow',
            'price': '29.99'
        }
    ]
    return jsonify({'success': True, 'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True) 