import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, send_from_directory
from functools import wraps
import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from ortools.linear_solver import pywraplp
import os
import requests
from functools import lru_cache
import traceback
import sys
import logging
import time
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.debug = True  # Enable debug mode

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO to reduce log noise
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Global variables for cached data
_model = None
_product_data = None
_product_info = None
_category_encoder = None
_data_loaded = False
_data_loading_lock = threading.Lock()

def load_data_in_background():
    """Load data in a background thread to avoid blocking the main application"""
    global _model, _product_data, _product_info, _category_encoder, _data_loaded
    
    with _data_loading_lock:
        if not _data_loaded:
            try:
                logger.info("Starting background data loading...")
                
                # Load model
                start_time = time.time()
                with open('data/random_forest_model.pkl', 'rb') as file:
                    _model = pickle.load(file)
                logger.info(f"Model loaded in {time.time() - start_time:.2f} seconds")
                logger.info(f"Model feature names: {_model.feature_names_in_}")
                
                # Load and preprocess data
                start_time = time.time()
                _product_data = pd.read_csv('data/reddit_product_embeddings.csv')
                _product_info = pd.read_csv('data/cleaned_makeup_products.csv')
                
                # Clean and validate URLs in product info
                logger.info("Cleaning and validating URLs...")
                _product_info['product_link'] = _product_info['product_link'].apply(lambda x: clean_url(x))
                
                # Log URL statistics
                total_urls = len(_product_info)
                valid_urls = _product_info['product_link'].notna().sum()
                logger.info(f"URL Statistics: {valid_urls}/{total_urls} valid URLs")
                
                # Log invalid URLs
                invalid_urls = _product_info[_product_info['product_link'].isna()]
                if not invalid_urls.empty:
                    logger.warning(f"Found {len(invalid_urls)} products with invalid URLs:")
                    for idx, row in invalid_urls.iterrows():
                        logger.warning(f"Product: {row['product_name']}, Original URL: {row['product_link']}")
                
                # Initialize and fit category encoder
                logger.info("Initializing category encoder...")
                _category_encoder = LabelEncoder()
                logger.info(f"Category encoder initialized: {_category_encoder}")
                
                # Ensure category column exists and has data
                if 'category' not in _product_data.columns:
                    raise ValueError("Category column not found in product data")
                
                logger.info(f"Unique categories before encoding: {_product_data['category'].unique()}")
                _category_encoder.fit(_product_data['category'])
                logger.info(f"Category encoder fitted. Classes: {_category_encoder.classes_}")
                
                # Pre-process product info
                _product_info = _product_info[['product_link_id', 'product_name', 'brand', 'price',
                                             'category', 'description', 'product_link']]
                _product_info.rename(columns={'category': 'category_name'}, inplace=True)
                
                # Verify model features exist in product data
                model_features = set(_model.feature_names_in_)
                data_features = set(_product_data.columns)
                
                # Create review features from existing features
                review_features = {
                    'young_review': 'young',
                    'mother_review': 'mother',
                    'professional_review': 'professional',
                    'vibe_review': 'vibe',
                    'acne_review': 'acne',
                    'dry_review': 'dry',
                    'wrinkles_review': 'wrinkles',
                    'black_review': 'black',
                    'white_review': 'white',
                    'tan_review': 'tan',
                    'redness_review': 'redness',
                    'light_coverage_review': 'light_coverage',
                    'medium_coverage_review': 'medium_coverage',
                    'full_coverage_review': 'full_coverage',
                    'skin_concerns_review': 'skin_concerns',
                    'comfortable_wear_review': 'comfortable_wear',
                    'easy_use_review': 'easy_use'
                }
                
                # Add review features to product data
                for review_feature, base_feature in review_features.items():
                    if base_feature in _product_data.columns:
                        _product_data[review_feature] = _product_data[base_feature]
                
                # Update data features after adding review features
                data_features = set(_product_data.columns)
                missing_features = model_features - data_features
                if missing_features:
                    logger.error(f"Missing features in product data: {missing_features}")
                    raise ValueError(f"Missing features in product data: {missing_features}")
                
                logger.info(f"Data loaded and preprocessed in {time.time() - start_time:.2f} seconds")
                
                # Verify all components are properly initialized
                if _model is None:
                    raise ValueError("Model not loaded")
                if _product_data is None:
                    raise ValueError("Product data not loaded")
                if _product_info is None:
                    raise ValueError("Product info not loaded")
                if _category_encoder is None:
                    raise ValueError("Category encoder not initialized")
                
                # Only set _data_loaded to True if everything is successful
                _data_loaded = True
                logger.info("Data loading completed successfully")
                
            except Exception as e:
                logger.error(f"Error loading data: {str(e)}")
                logger.error(traceback.format_exc())
                _data_loaded = False  # Reset the flag on error
                _model = None
                _product_data = None
                _product_info = None
                _category_encoder = None
                raise

def clean_url(url):
    """Clean and validate a URL"""
    if pd.isna(url) or url == '#' or not isinstance(url, str):
        return None
    
    # Remove any whitespace
    url = url.strip()
    
    # Check if URL is already valid
    if url.startswith(('http://', 'https://')):
        return url
    
    # Try to make URL valid
    try:
        # Add https:// if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Basic URL validation
        if not url.startswith(('http://', 'https://')):
            logger.warning(f"Invalid URL format: {url}")
            return None
            
        return url
    except Exception as e:
        logger.warning(f"Error cleaning URL {url}: {str(e)}")
        return None

def get_model():
    """Get the model, loading it if necessary"""
    global _model
    if _model is None:
        load_data_in_background()
    return _model

def get_product_data():
    """Get the product data, loading it if necessary"""
    global _product_data, _product_info, _category_encoder
    
    if not _data_loaded:
        logger.info("Data not loaded, loading now...")
        load_data_in_background()
    
    if _product_data is None or _product_info is None or _category_encoder is None:
        logger.error("Data components are None even though _data_loaded is True")
        logger.error(f"Product data: {_product_data is not None}")
        logger.error(f"Product info: {_product_info is not None}")
        logger.error(f"Category encoder: {_category_encoder is not None}")
        raise ValueError("Data components not properly initialized")
    
    return _product_data, _product_info, _category_encoder

# Load data before starting the application
logger.info("Starting data loading...")
try:
    load_data_in_background()
    logger.info("Initial data loading completed successfully")
except Exception as e:
    logger.error(f"Failed to load initial data: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Performance monitoring decorator
def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        if end_time - start_time > 0.1:  # Only log if operation takes more than 100ms
            logger.info(f"{func.__name__} took {end_time - start_time:.2f} seconds to execute")
        return result
    return wrapper

# Mock user database (replace with real database in production)
users = {
    'demo@example.com': {'password': 'demo123'}
}

# Error handler
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}")
    logger.error(traceback.format_exc())
    return render_template('error.html', error=str(error)), 500

@app.errorhandler(Exception)
def handle_exception(error):
    logger.error(f"Unhandled Exception: {str(error)}")
    logger.error(traceback.format_exc())
    return render_template('error.html', error=str(error)), 500

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Cache decorators to replace st.cache
def cache_resource(func):
    return lru_cache(maxsize=None)(func)

def cache_data(func):
    return lru_cache(maxsize=None)(func)

# Application Constants
AGE_RANGES = ['Under 20', '20-30', '30-40', '40-50', '50+']
SKIN_TYPES = ['Oily', 'Dry', 'Combination']
EXPERIENCE_LEVELS = ['Beginner', 'Intermediate', 'Pro']
COVERAGE_TYPES = ['Light', 'Medium', 'Full']
LIFESTYLE_OPTIONS = ['Working Professional', 'Mom/Parent', 'Student', 'Retired']
BUSY_LEVELS = ['1 - Not Busy/Active', '2 - Moderately Busy/Active', '3 - Super Busy/Active']

SKIN_TONE_OPTIONS = {
    'Light': 'fair-palette.svg',
    'Medium': 'medium-palette.svg',
    'Deep': 'deep-palette.svg'
}

SKIN_CONDITIONS = {
    'Wrinkles': 'wrinkles.jpg',
    'Acne': 'acne.jpg',
    'Hyperpigmentation': 'hyperpigmentation.jpg',
    'Dark Circles': 'dark_circles.jpg',
    'Redness/Rosacea': 'redness.jpg',
    'Sensitive Skin': 'sensitive.jpg'
}

@log_execution_time
def get_user_profile(form_data):
    try:
        logger.debug("=== DEBUG: Form Data in get_user_profile ===")
        logger.debug("Age Range:", form_data.get('age_range'))
        logger.debug("Skin Type:", form_data.get('skin_type'))
        logger.debug("Skin Tone:", form_data.get('skin_tone'))
        logger.debug("Coverage:", form_data.get('coverage'))
        logger.debug("Experience Level:", form_data.get('experience_level'))
        logger.debug("Activity Level:", form_data.get('activity_level'))
        logger.debug("Lifestyle:", form_data.getlist('lifestyle'))
        logger.debug("Conditions:", form_data.getlist('conditions'))
        
        age_range = form_data.get('age_range')
        if not age_range:
            raise ValueError("Age range is required")
            
        skin_type = form_data.get('skin_type')
        if not skin_type:
            raise ValueError("Skin type is required")
            
        selected_skin_tone = form_data.get('skin_tone')
        if not selected_skin_tone:
            raise ValueError("Skin tone is required")
            
        coverage = form_data.get('coverage')
        if not coverage:
            raise ValueError("Coverage is required")
            
        experience_level = form_data.get('experience_level')
        if not experience_level:
            raise ValueError("Experience level is required")
            
        active_options = form_data.get('activity_level')
        if not active_options:
            raise ValueError("Activity level is required")
            
        lifestyle_options = form_data.getlist('lifestyle')
        selected_conditions = form_data.getlist('conditions')
        
        # Convert skin conditions to dict
        user_conditions = {condition: condition in selected_conditions
                         for condition in SKIN_CONDITIONS.keys()}
        
        profile = {
            'professional_review': 1 if 'Working Professional' in lifestyle_options else 0,
            'vibe_review': 1 if 'Retired' in lifestyle_options or age_range in ['40-50', '50+'] else 0,
            'redness_review': 1 if user_conditions.get('Redness/Rosacea', False) else 0,
            'dry_review': 1 if skin_type == 'Dry' else 0.5 if skin_type == 'Combination' else 0,
            'light_coverage_review': 1 if coverage == 'Light' else 0,
            'young_review': 1 if age_range in ['Under 20', '20-30'] or 'Student' in lifestyle_options else 0,
            'mother_review': 1 if 'Mom/Parent' in lifestyle_options else 0,
            'skin_concerns_review': 1 if any(user_conditions.values()) else 0,
            'white_review': 1 if selected_skin_tone == 'Light' else 0,
            'tan_review': 1 if selected_skin_tone == 'Medium' else 0,
            'acne_review': 1 if user_conditions.get('Acne', False) or skin_type == 'Oily' else 0.5 if skin_type == 'Combination' else 0,
            'black_review': 1 if selected_skin_tone == 'Deep' else 0,
            'comfortable_wear_review': 1 if 'Working Professional' in lifestyle_options or active_options == '3 - Super Busy/Active' else 0.5 if active_options == '2 - Moderately Busy/Active' else 0,
            'coverage_review': 0 if coverage in ['Medium', 'Full'] else 1,
            'medium_coverage_review': 1 if coverage == 'Medium' else 0,
            'full_coverage_review': 1 if coverage == 'Full' else 0,
            'easy_use_review': 1 if experience_level == 'Beginner' else 0,
            'wrinkles_review': 1 if user_conditions.get('Wrinkles', False) else 0
        }
        
        logger.debug("=== DEBUG: Generated Profile ===")
        logger.debug(profile)
        return profile
        
    except Exception as e:
        logger.error(f"Error in get_user_profile: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@log_execution_time
def get_product_recommendations(user_profile, max_budget):
    try:
        logger.info("Starting get_product_recommendations")
        logger.info(f"User profile: {user_profile}")
        logger.info(f"Max budget: {max_budget}")
        
        # Get cached data
        product_data, product_info, category_encoder = get_product_data()
        model = get_model()
        
        logger.info("Data loaded successfully")
        logger.info(f"Product data columns: {product_data.columns.tolist()}")
        logger.info(f"Model feature names: {model.feature_names_in_}")
        
        # Convert INR budget to USD (1 USD ≈ 83 INR)
        USD_TO_INR_RATE = 83
        max_budget_usd = max_budget / USD_TO_INR_RATE
        
        # Create a new DataFrame with all features needed for prediction
        feature_names = model.feature_names_in_  # Include all features, including category
        logger.info(f"Features needed for prediction: {feature_names}")
        
        # Create a DataFrame with all required features initialized to 0.0
        product_copy = pd.DataFrame(0.0, index=product_data.index, columns=feature_names)
        
        # Add user profile features
        for col, val in user_profile.items():
            if col in feature_names:
                product_copy[col] = float(val)
        
        # Add product features that exist in both datasets
        for feature in feature_names:
            if feature == 'category':
                # Handle category feature separately - encode it using the category_encoder
                try:
                    logger.info(f"Encoding categories. Unique categories: {product_data['category'].unique()}")
                    product_copy['category'] = category_encoder.transform(product_data['category'])
                    logger.info(f"Category encoding successful. Encoded values: {product_copy['category'].unique()}")
                except Exception as e:
                    logger.error(f"Error encoding categories: {str(e)}")
                    logger.error(f"Category encoder state: {category_encoder.__dict__}")
                    raise
            elif feature in product_data.columns:
                try:
                    product_copy[feature] = pd.to_numeric(product_data[feature], errors='coerce').fillna(0.0)
                except Exception as e:
                    logger.error(f"Error converting feature {feature}: {str(e)}")
                    product_copy[feature] = 0.0
        
        # Verify all features are float type (including category since it's now encoded)
        for feature in feature_names:
            product_copy[feature] = product_copy[feature].astype(float)
        
        logger.info("Making predictions...")
        try:
            predictions = model.predict_proba(product_copy)
            logger.info("Predictions made successfully")
        except Exception as e:
            logger.error(f"Error making predictions: {str(e)}")
            logger.error(f"Data types: {product_copy.dtypes}")
            logger.error(f"Sample data: {product_copy.head()}")
            raise
        
        # Create result DataFrame
        result_df = pd.DataFrame({
            'product_link_id': product_data['product_link_id'],
            'predicted_score': predictions[:, 0] + 2 * predictions[:, 1] + 3 * predictions[:, 2] + 4 * predictions[:, 3] + 5 * predictions[:, 4]
        })
        
        # Merge with product info
        product_budget = pd.merge(result_df, product_info, how='inner', on='product_link_id')
        
        # Define categories and rules based on user profile
        skin_categories = ['Foundation', 'Tinted Moisturizer', 'BB & CC Creams']
        allowed_skin_categories = []
        allowed_makeup_products = []
        
        if user_profile['light_coverage_review']:
            allowed_makeup_products = ['Blush', 'Concealer', 'Makeup Remover', 'Setting Spray & Powder']
            if user_profile['easy_use_review']:
                allowed_skin_categories = ['Foundation', 'Tinted Moisturizer']
            elif user_profile['acne_review']:
                allowed_skin_categories = ['Foundation', 'BB & CC Creams']
            elif user_profile['comfortable_wear_review']:
                allowed_skin_categories = ['Tinted Moisturizer', 'BB & CC Creams']
            else:
                allowed_skin_categories = ['Foundation', 'Tinted Moisturizer', 'BB & CC Creams']
        elif user_profile['medium_coverage_review']:
            allowed_makeup_products = ['Face Primer', 'Blush', 'Bronzer', 'Concealer', 'Makeup Remover', 'Setting Spray & Powder']
            allowed_skin_categories = ['Foundation', 'BB & CC Creams']
        elif user_profile['full_coverage_review']:
            allowed_makeup_products = ['Face Primer', 'Blush', 'Bronzer', 'Contouring', 'Highlighter', 'Color Correcting', 'Concealer', 'Makeup Remover', 'Setting Spray & Powder']
            allowed_skin_categories = ['Foundation']
        
        # Filter products based on allowed categories
        product_budget = product_budget[
            (product_budget['category_name'].isin(allowed_skin_categories)) |
            (product_budget['category_name'].isin(allowed_makeup_products))
        ]
        
        # Filter by budget
        product_budget = product_budget[product_budget['price'] <= max_budget_usd]
        
        # Sort by predicted score and get top recommendations
        recommendations = product_budget.sort_values('predicted_score', ascending=False).head(8)
        
        # Format recommendations
        formatted_recommendations = []
        for _, row in recommendations.iterrows():
            url = row['product_link']
            logger.info(f"Processing URL for {row['product_name']}: {url}")
            
            formatted_recommendations.append({
                'Category': row['category_name'],
                'Product Name': row['product_name'],
                'Price': f"₹{row['price'] * USD_TO_INR_RATE:.2f}",
                'URL': url
            })
        
        logger.info(f"Generated {len(formatted_recommendations)} recommendations")
        return formatted_recommendations
        
    except Exception as e:
        logger.error(f"Error in get_product_recommendations: {str(e)}")
        logger.error(traceback.format_exc())
        raise

@app.route('/')
def index():
    try:
        logger.info("Rendering index.html")
        # Include all necessary context variables
        context = {
            'title': 'SkinGenie - Your Personal Beauty Guide',
            'debug': app.debug,
            'age_ranges': AGE_RANGES,
            'skin_types': SKIN_TYPES,
            'experience_levels': EXPERIENCE_LEVELS,
            'coverage_types': COVERAGE_TYPES,
            'lifestyle_options': LIFESTYLE_OPTIONS,
            'busy_levels': BUSY_LEVELS,
            'skin_tone_options': SKIN_TONE_OPTIONS,
            'skin_conditions': SKIN_CONDITIONS
        }
        return render_template('index.html', **context)
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error=str(e)), 500

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
        
        if not email or not password or not confirm_password or not fullname:
            flash('All fields are required', 'error')
            return redirect(url_for('signup'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        
        if email in users:
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
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

@app.route('/survey')
def survey():
    try:
        logger.info("Rendering survey.html")
        # Include all necessary context variables
        context = {
            'title': 'SkinGenie - Find Your Match',
            'age_ranges': AGE_RANGES,
            'skin_types': SKIN_TYPES,
            'experience_levels': EXPERIENCE_LEVELS,
            'coverage_types': COVERAGE_TYPES,
            'lifestyle_options': LIFESTYLE_OPTIONS,
            'busy_levels': BUSY_LEVELS,
            'skin_tone_options': SKIN_TONE_OPTIONS,
            'skin_conditions': SKIN_CONDITIONS
        }
        return render_template('survey.html', **context)
    except Exception as e:
        logger.error(f"Error in survey route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error=str(e)), 500

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    try:
        form_data = request.form
        max_budget = float(form_data.get('max_budget', 1000))
        
        # Generate user profile
        user_profile = get_user_profile(form_data)
        
        # Get product recommendations
        recommendations = get_product_recommendations(user_profile, max_budget)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations
        })
    except Exception as e:
        logger.error(f"Error in get_recommendations route: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/favicon.ico')
def favicon():
    try:
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    except Exception as e:
        # If favicon.ico doesn't exist, return a 204 No Content response
        return '', 204

@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # Debug: Print all form data
        logger.debug("=== DEBUG: Form Data ===")
        for key, value in request.form.items():
            logger.debug(f"{key}: {value}")
        
        form_data = request.form
        try:
            max_budget = float(form_data.get('max_budget', 20))
            logger.debug(f"=== DEBUG: Max Budget ===\n{max_budget}")
        except ValueError as e:
            logger.error(f"Error converting max_budget: {str(e)}")
            return jsonify({
                'error': f"Invalid budget value: {form_data.get('max_budget')}"
            }), 400
        
        # Generate user profile with detailed error handling
        try:
            logger.debug("=== DEBUG: Generating User Profile ===")
            user_profile = get_user_profile(form_data)
            logger.debug(f"User Profile: {user_profile}")
        except Exception as e:
            logger.error(f"Error in get_user_profile: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f"Error generating user profile: {str(e)}"
            }), 400
        
        # Get product recommendations with detailed error handling and timeout
        try:
            logger.debug("=== DEBUG: Getting Product Recommendations ===")
            logger.debug(f"Input - User Profile: {user_profile}")
            logger.debug(f"Input - Max Budget: {max_budget}")
            
            # Set a timeout for the recommendation process
            timeout = 30  # seconds
            start_time = time.time()
            
            # Check if data is loaded
            if not _data_loaded:
                logger.info("Waiting for data to load...")
                while not _data_loaded and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                if not _data_loaded:
                    raise TimeoutError("Data loading timed out")
            
            # Verify all components are loaded
            if _model is None or _product_data is None or _product_info is None or _category_encoder is None:
                raise ValueError("Required data components not loaded")
            
            recommendations = get_product_recommendations(user_profile, max_budget)
            logger.debug(f"Generated {len(recommendations)} recommendations")
            
            if not recommendations:
                return jsonify({
                    'error': "No recommendations found matching your criteria"
                }), 404
                
            # Check if the request is coming from a browser (Accept header contains text/html)
            # or from an AJAX call (expecting JSON)
            if request.headers.get('Accept', '').find('text/html') >= 0 and request.headers.get('X-Requested-With') != 'XMLHttpRequest':
                # This is a direct form submission, render the results page
                return render_template('results.html', 
                                     recommendations=recommendations,
                                     title="Your Personalized Recommendations")
            else:
                # This is an AJAX call, return JSON
                return jsonify(recommendations)
            
        except TimeoutError as e:
            logger.error(f"Timeout error: {str(e)}")
            return jsonify({
                'error': "The recommendation process took too long. Please try again."
            }), 408
        except Exception as e:
            logger.error(f"Error in get_product_recommendations: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'error': f"Error generating recommendations: {str(e)}"
            }), 500
            
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return jsonify({'error': error_msg}), 500

@app.route('/about')
def about():
    try:
        logger.info("Rendering about.html")
        return render_template('about.html')
    except Exception as e:
        logger.error(f"Error in about route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error=str(e)), 500

@app.route('/contact')
def contact():
    try:
        logger.info("Rendering contact.html")
        return render_template('contact.html')
    except Exception as e:
        logger.error(f"Error in contact route: {str(e)}")
        logger.error(traceback.format_exc())
        return render_template('error.html', error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 