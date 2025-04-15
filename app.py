from flask import Flask
import os
from models import db, User
from blueprints import auth_bp, main_bp, dashboard_bp

# Create Flask application instance
# Set folders for static files and templates
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure application settings
# Secret key is used for session security
app.config['SECRET_KEY'] = os.urandom(24)
# SQLite database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Disable modification tracking to improve performance
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with the Flask app
db.init_app(app)

# Register blueprints to organize routes by feature
app.register_blueprint(main_bp)      # Main pages (homepage, etc.)
app.register_blueprint(auth_bp)      # Authentication (login, register, logout)
app.register_blueprint(dashboard_bp) # User dashboard features

# Create database tables based on the models
with app.app_context():
    db.create_all()

# Run the application when executed directly
if __name__ == '__main__':
    # Enable debug mode for development (disable in production)
    app.run(debug=True) 