from flask import Blueprint, render_template, session, redirect, url_for, flash

# Create a Blueprint for user dashboard and related features
# 'dashboard' is the name of this Blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Dashboard main view - shows user profile and recommendations
@dashboard_bp.route('/dashboard')
def view():
    # Check if user is logged in
    if 'user_id' not in session:
        # If not logged in, redirect to login page with error message
        flash('Please login first!', 'error')
        return redirect(url_for('auth.login'))
    
    # Render dashboard template for logged-in users
    return render_template('dashboard.html')

# Wishlist view - shows user's saved products
@dashboard_bp.route('/wishlist')
def wishlist():
    # Check if user is logged in
    if 'user_id' not in session:
        # If not logged in, redirect to login page with error message
        flash('Please login first!', 'error')
        return redirect(url_for('auth.login'))
    
    # Render wishlist template for logged-in users
    return render_template('wishlist.html') 