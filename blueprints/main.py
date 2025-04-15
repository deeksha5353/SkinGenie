from flask import Blueprint, render_template

# Create a Blueprint for main pages
# 'main' is the name of this Blueprint
# __name__ is the name of the current module
main_bp = Blueprint('main', __name__)

# Route for homepage
@main_bp.route('/')
def index():
    # Render the index.html template from the templates folder
    return render_template('index.html') 