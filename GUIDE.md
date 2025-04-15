# SkinGenie Developer Guide

This guide will help you understand how to work with the SkinGenie application. It explains the most common tasks and how to implement them.

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python app.py`
4. Open your browser at: http://127.0.0.1:5000/

## Common Tasks

### How to Add a New Page

1. **Create the HTML Template**
   
   Create a new HTML file in the `templates` folder, for example `new_page.html`:
   ```html
   {% extends "base.html" %}
   {% block content %}
     <h1>New Page</h1>
     <p>This is my new page content.</p>
   {% endblock %}
   ```

2. **Add a Route to a Blueprint**
   
   Decide which blueprint should handle this page. For general pages, use `main.py`:
   ```python
   @main_bp.route('/new-page')
   def new_page():
       return render_template('new_page.html')
   ```

3. **Add Navigation Links**
   
   Update navigation links in templates:
   ```html
   <li><a href="{{ url_for('main.new_page') }}">New Page</a></li>
   ```

### How to Add CSS Styles

1. Either add to existing CSS files in `static/css/` or create a new one
2. Link the CSS in your HTML templates:
   ```html
   <link rel="stylesheet" href="{{ url_for('static', filename='css/your_style.css') }}">
   ```

### How to Add JavaScript Functions

1. Add to existing JS files in `static/js/` or create a new one
2. Link the JavaScript file in your HTML templates:
   ```html
   <script src="{{ url_for('static', filename='js/your_script.js') }}"></script>
   ```

### How to Add a Database Model

1. Edit `models.py` to add a new model class:
   ```python
   class Product(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       name = db.Column(db.String(100), nullable=False)
       price = db.Column(db.Float, nullable=False)
       description = db.Column(db.Text)
       # Add a relationship with User if needed
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       user = db.relationship('User', backref=db.backref('products', lazy=True))
   ```

2. Create the database tables by running your app once with:
   ```python
   with app.app_context():
       db.create_all()
   ```

### How to Add a New Form

1. Create a form using Flask-WTF in a new `forms.py` file:
   ```python
   from flask_wtf import FlaskForm
   from wtforms import StringField, TextAreaField, SubmitField
   from wtforms.validators import DataRequired, Email

   class ContactForm(FlaskForm):
       name = StringField('Name', validators=[DataRequired()])
       email = StringField('Email', validators=[DataRequired(), Email()])
       message = TextAreaField('Message', validators=[DataRequired()])
       submit = SubmitField('Send Message')
   ```

2. Use the form in your route:
   ```python
   @main_bp.route('/contact', methods=['GET', 'POST'])
   def contact():
       form = ContactForm()
       if form.validate_on_submit():
           # Process the form data
           flash('Message sent successfully!', 'success')
           return redirect(url_for('main.index'))
       return render_template('contact.html', form=form)
   ```

### How to Add User Authentication Features

1. The basic authentication system is already set up in `auth.py`
2. To require login for a page, add this check to your route:
   ```python
   @main_bp.route('/protected-page')
   def protected_page():
       if 'user_id' not in session:
           flash('Please login first!', 'error')
           return redirect(url_for('auth.login'))
       # Your code for logged-in users
       return render_template('protected_page.html')
   ```

## Project Structure Overview

- `app.py`: Main application file
- `models.py`: Database models
- `blueprints/`: Route modules organized by feature
- `templates/`: HTML templates
- `static/`: CSS, JavaScript, images
  - `css/`: Stylesheet files
  - `js/`: JavaScript files
  - `images/`: Image files

## Coding Standards

1. Use descriptive variable and function names
2. Add comments to explain complex logic
3. Follow PEP 8 style guide for Python code
4. Use Flask's url_for() for all links instead of hardcoding URLs
5. Keep HTML, CSS, and JavaScript in separate files
6. Use blueprints to organize related routes

## Troubleshooting

- If templates aren't rendering, check the template folder path in `app.py`
- If static files aren't loading, check that you're using `url_for` correctly
- If database changes aren't reflected, you may need to delete and recreate the database file
- For routing errors, check that blueprints are registered in `app.py` 