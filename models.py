from flask_sqlalchemy import SQLAlchemy

# Create a SQLAlchemy database instance
# This will be initialized with the Flask app in app.py
db = SQLAlchemy()

# User model - stores user account information
class User(db.Model):
    # Primary key for user identification
    id = db.Column(db.Integer, primary_key=True)
    
    # User email - must be unique for login purposes
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Hashed password - never store plain text passwords
    password = db.Column(db.String(200), nullable=False)
    
    # You can add more user fields here as needed:
    # Example:
    # name = db.Column(db.String(100))
    # skin_type = db.Column(db.String(50))
    # skin_tone = db.Column(db.String(50)) 