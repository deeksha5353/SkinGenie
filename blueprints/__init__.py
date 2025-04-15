# Import all blueprints here for easy access
# This allows importing multiple blueprints from the blueprints directory
# Example: from blueprints import auth_bp, main_bp

# Authentication blueprint for login, signup, logout functions
from .auth import auth_bp

# Main blueprint for the homepage and other main pages
from .main import main_bp

# Dashboard blueprint for user profile and features
from .dashboard import dashboard_bp

# When adding a new blueprint:
# 1. Create a new file in this directory (e.g., products.py)
# 2. Define your blueprint in that file
# 3. Import it here (e.g., from .products import products_bp)
# 4. Register it in app.py 