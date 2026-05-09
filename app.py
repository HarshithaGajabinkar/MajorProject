# app.py - UPDATED WITH HOSPITAL DATA DIRECTLY INCLUDED
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import joblib
import numpy as np
import pandas as pd
import json
from config import Config
import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Add the utils directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Create Flask app FIRST
app = Flask(__name__)
app.config.from_object(Config)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

# Now import db from models AFTER creating app
from models import db

# Initialize database with app
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Import User model AFTER db is initialized
from models import User, Prediction
from forms import RegistrationForm, LoginForm

# ============================================================================
# HOSPITAL DATA - DIRECTLY INCLUDED (NO SEPARATE FILE NEEDED)
# ============================================================================

HUZURABAD_HOSPITALS = [
    {
        "Hospital_ID": "HZR001",
        "Hospital_Name": "Government Area Hospital, Huzurabad",
        "Address": "Near Bus Stand, Huzurabad, Telangana 505468",
        "Type": "Government",
        "Specialties": "General Medicine, Emergency, Maternity, Pediatrics, Surgery",
        "Beds_Total": 100,
        "ICU_Beds": 10,
        "Ventilators": 5,
        "Contact_Number": "08728-255555",
        "Emergency_Contact": "08728-255556",
        "Email": "gah.huzurabad@telangana.gov.in",
        "Website": "",
        "Latitude": 18.2046,
        "Longitude": 79.4997,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "Yes",
        "Pharmacy": "Yes",
        "Rating": 4.2,
        "Established_Year": 1985,
        "Distance": "1.2 km",
        "Travel_Time": "5 minutes"
    },
    {
        "Hospital_ID": "HZR002",
        "Hospital_Name": "Sri Sai Ram Hospital",
        "Address": "Station Road, Huzurabad, Telangana 505468",
        "Type": "Private",
        "Specialties": "General Surgery, Pediatrics, Orthopedics, Cardiology",
        "Beds_Total": 75,
        "ICU_Beds": 8,
        "Ventilators": 4,
        "Contact_Number": "08728-266666",
        "Emergency_Contact": "08728-266667",
        "Email": "srisairam.hzr@gmail.com",
        "Website": "",
        "Latitude": 18.2050,
        "Longitude": 79.5000,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.4,
        "Established_Year": 1995,
        "Distance": "1.5 km",
        "Travel_Time": "7 minutes"
    },
    {
        "Hospital_ID": "HZR003",
        "Hospital_Name": "Geetha Hospital",
        "Address": "Near RTC Bus Stand, Huzurabad",
        "Type": "Private",
        "Specialties": "General Medicine, Gynecology, Pediatrics",
        "Beds_Total": 50,
        "ICU_Beds": 4,
        "Ventilators": 2,
        "Contact_Number": "08728-277777",
        "Emergency_Contact": "08728-277778",
        "Email": "",
        "Website": "",
        "Latitude": 18.2060,
        "Longitude": 79.5010,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.1,
        "Established_Year": 2000,
        "Distance": "2.0 km",
        "Travel_Time": "8 minutes"
    },
    {
        "Hospital_ID": "HZR004",
        "Hospital_Name": "Swathi Hospital",
        "Address": "Huzurabad Main Road, Near Clock Tower",
        "Type": "Private",
        "Specialties": "General Medicine, ENT, Dermatology",
        "Beds_Total": 40,
        "ICU_Beds": 3,
        "Ventilators": 1,
        "Contact_Number": "08728-288888",
        "Emergency_Contact": "08728-288889",
        "Email": "",
        "Website": "",
        "Latitude": 18.2035,
        "Longitude": 79.4985,
        "Operating_Hours": "8:00 AM - 10:00 PM",
        "Ambulance_Service": "No",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 3.9,
        "Established_Year": 2005,
        "Distance": "0.8 km",
        "Travel_Time": "4 minutes"
    },
    {
        "Hospital_ID": "HZR005",
        "Hospital_Name": "Raghava Nursing Home",
        "Address": "Market Road, Huzurabad",
        "Type": "Private",
        "Specialties": "General Medicine, Pediatrics",
        "Beds_Total": 25,
        "ICU_Beds": 2,
        "Ventilators": 0,
        "Contact_Number": "08728-299999",
        "Emergency_Contact": "08728-299990",
        "Email": "",
        "Website": "",
        "Latitude": 18.2070,
        "Longitude": 79.5020,
        "Operating_Hours": "9:00 AM - 9:00 PM",
        "Ambulance_Service": "No",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 3.8,
        "Established_Year": 2008,
        "Distance": "2.5 km",
        "Travel_Time": "10 minutes"
    },
    {
        "Hospital_ID": "HZR006",
        "Hospital_Name": "Nagarjuna Hospital",
        "Address": "Bus Stand Road, Huzurabad",
        "Type": "Private",
        "Specialties": "General Medicine, Orthopedics, Physiotherapy",
        "Beds_Total": 35,
        "ICU_Beds": 3,
        "Ventilators": 1,
        "Contact_Number": "08728-244444",
        "Emergency_Contact": "08728-244445",
        "Email": "nagarjunahosp.hzr@yahoo.com",
        "Website": "",
        "Latitude": 18.2025,
        "Longitude": 79.4975,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.0,
        "Established_Year": 2010,
        "Distance": "1.8 km",
        "Travel_Time": "7 minutes"
    },
    {
        "Hospital_ID": "HZR007",
        "Hospital_Name": "Srinivasa Hospital",
        "Address": "Karimnagar Road, Huzurabad",
        "Type": "Private",
        "Specialties": "Multi-specialty, Cardiology, Neurology",
        "Beds_Total": 60,
        "ICU_Beds": 6,
        "Ventilators": 3,
        "Contact_Number": "08728-233333",
        "Emergency_Contact": "08728-233334",
        "Email": "srinivasahosp.hzr@gmail.com",
        "Website": "",
        "Latitude": 18.2010,
        "Longitude": 79.4960,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "Yes",
        "Pharmacy": "Yes",
        "Rating": 4.3,
        "Established_Year": 2012,
        "Distance": "2.2 km",
        "Travel_Time": "9 minutes"
    },
    {
        "Hospital_ID": "HZR008",
        "Hospital_Name": "Medwin Hospital",
        "Address": "Near Police Station, Huzurabad",
        "Type": "Private",
        "Specialties": "General Medicine, Surgery, Ophthalmology",
        "Beds_Total": 45,
        "ICU_Beds": 4,
        "Ventilators": 2,
        "Contact_Number": "08728-222222",
        "Emergency_Contact": "08728-222223",
        "Email": "",
        "Website": "",
        "Latitude": 18.2080,
        "Longitude": 79.5030,
        "Operating_Hours": "24/7",
        "Ambulance_Service": "Yes",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.1,
        "Established_Year": 2015,
        "Distance": "2.8 km",
        "Travel_Time": "12 minutes"
    },
    {
        "Hospital_ID": "HZR009",
        "Hospital_Name": "Huzurabad Eye Hospital",
        "Address": "Near Municipal Office, Huzurabad",
        "Type": "Specialty",
        "Specialties": "Ophthalmology, Cataract Surgery, LASIK",
        "Beds_Total": 20,
        "ICU_Beds": 1,
        "Ventilators": 0,
        "Contact_Number": "08728-211111",
        "Emergency_Contact": "08728-211112",
        "Email": "eyehosp.hzr@gmail.com",
        "Website": "",
        "Latitude": 18.2090,
        "Longitude": 79.5040,
        "Operating_Hours": "9:00 AM - 8:00 PM",
        "Ambulance_Service": "No",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.5,
        "Established_Year": 2018,
        "Distance": "3.0 km",
        "Travel_Time": "13 minutes"
    },
    {
        "Hospital_ID": "HZR010",
        "Hospital_Name": "Dental Care Hospital",
        "Address": "Center Point, Huzurabad",
        "Type": "Specialty",
        "Specialties": "Dentistry, Orthodontics, Oral Surgery",
        "Beds_Total": 10,
        "ICU_Beds": 0,
        "Ventilators": 0,
        "Contact_Number": "08728-200000",
        "Emergency_Contact": "08728-200001",
        "Email": "",
        "Website": "",
        "Latitude": 18.2000,
        "Longitude": 79.4950,
        "Operating_Hours": "10:00 AM - 7:00 PM",
        "Ambulance_Service": "No",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 4.2,
        "Established_Year": 2020,
        "Distance": "2.3 km",
        "Travel_Time": "10 minutes"
    },
    {
        "Hospital_ID": "HZR011",
        "Hospital_Name": "Primary Health Center (PHC), Huzurabad",
        "Address": "Main Road, Huzurabad",
        "Type": "Government",
        "Specialties": "Primary Care, Immunization, Basic Medicine",
        "Beds_Total": 15,
        "ICU_Beds": 0,
        "Ventilators": 0,
        "Contact_Number": "08728-266555",
        "Emergency_Contact": "08728-266556",
        "Email": "",
        "Website": "",
        "Latitude": 18.2040,
        "Longitude": 79.5005,
        "Operating_Hours": "9:00 AM - 5:00 PM",
        "Ambulance_Service": "No",
        "Blood_Bank": "No",
        "Pharmacy": "Yes",
        "Rating": 3.7,
        "Established_Year": 1990,
        "Distance": "1.0 km",
        "Travel_Time": "4 minutes"
    }
]

def get_hospitals_by_severity(severity):
    """
    Filter hospitals based on disease severity
    """
    all_hospitals = HUZURABAD_HOSPITALS.copy()
    
    if severity == "High":
        # For high severity: show only 24/7 hospitals, sorted by rating
        filtered = [h for h in all_hospitals if h["Operating_Hours"] == "24/7"]
        filtered.sort(key=lambda x: x["Rating"], reverse=True)
        return filtered[:6]  # Top 6 hospitals
    
    else:
        # For medium/low severity: show top hospitals by rating
        all_hospitals.sort(key=lambda x: x["Rating"], reverse=True)
        return all_hospitals[:8]  # Top 8 hospitals

def get_all_hospitals():
    """
    Return all hospitals sorted by rating
    """
    sorted_hospitals = HUZURABAD_HOSPITALS.copy()
    sorted_hospitals.sort(key=lambda x: x["Rating"], reverse=True)
    return sorted_hospitals

def get_hospital_stats():
    """
    Return statistics about hospitals
    """
    govt_count = len([h for h in HUZURABAD_HOSPITALS if h["Type"] == "Government"])
    private_count = len([h for h in HUZURABAD_HOSPITALS if h["Type"] == "Private"])
    specialty_count = len([h for h in HUZURABAD_HOSPITALS if h["Type"] == "Specialty"])
    
    total_beds = sum(h["Beds_Total"] for h in HUZURABAD_HOSPITALS)
    total_icu = sum(h["ICU_Beds"] for h in HUZURABAD_HOSPITALS)
    
    return {
        "total_hospitals": len(HUZURABAD_HOSPITALS),
        "government_hospitals": govt_count,
        "private_hospitals": private_count,
        "specialty_hospitals": specialty_count,
        "total_beds": total_beds,
        "total_icu_beds": total_icu,
        "24_7_hospitals": len([h for h in HUZURABAD_HOSPITALS if h["Operating_Hours"] == "24/7"])
    }

hospital_data_available = True

# ============================================================================
# END OF HOSPITAL DATA
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Load trained model, encoders, and precaution data
try:
    model = joblib.load('model/disease_model.pkl')
    label_encoder = joblib.load('model/label_encoder.pkl')
    symptom_encoder = joblib.load('model/symptom_encoder.pkl')
    all_symptoms = list(symptom_encoder.classes_)
    severity_df = pd.read_csv('data/disease_severity.csv')
    # Load precaution data
    try:
        precautions_df = pd.read_csv('data/symptom_precaution.csv')
    except FileNotFoundError:
        print("Warning: symptom_precaution.csv not found. Creating empty precautions dataframe.")
        precautions_df = pd.DataFrame()
except Exception as e:
    print(f"Error loading model files: {e}")
    model = None
    all_symptoms = []
    precautions_df = pd.DataFrame()

# Update forms to include database validation
def setup_forms():
    from models import User
    from wtforms.validators import ValidationError
    
    def new_validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')
    
    def new_validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered.')
    
    RegistrationForm.validate_username = new_validate_username
    RegistrationForm.validate_email = new_validate_email

# Call setup after app context is ready
with app.app_context():
    setup_forms()
# ===== JSON FILTER FOR JINJA2 =====
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []
# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's prediction history
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .limit(10).all()
    
    return render_template('dashboard.html', 
                         user=current_user,
                         predictions=predictions,
                         symptoms=all_symptoms)

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        if model is None:
            flash('Prediction model is not available.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get symptoms from form
        selected_symptoms = request.form.getlist('symptoms')
        
        if not selected_symptoms:
            flash("Please select at least one symptom", 'warning')
            return redirect(url_for('dashboard'))
        
        # Create input vector
        input_vector = np.zeros(len(all_symptoms))
        for symptom in selected_symptoms:
            if symptom in symptom_encoder.classes_:
                idx = list(symptom_encoder.classes_).index(symptom)
                input_vector[idx] = 1
        
        # Make prediction
        prediction = model.predict([input_vector])[0]
        disease_name = label_encoder.inverse_transform([prediction])[0]
        
        # Get disease severity
        severity_info = severity_df[severity_df['Disease'] == disease_name]
        severity = severity_info['Severity'].values[0] if not severity_info.empty else "Unknown"
        
        # Get probability scores for confidence
        probabilities = model.predict_proba([input_vector])[0]
        confidence = probabilities[prediction] * 100
        
        # Get precautions for the predicted disease
        precautions = []
        try:
            if not precautions_df.empty and 'Disease' in precautions_df.columns:
                disease_precautions = precautions_df[precautions_df['Disease'] == disease_name]
                if not disease_precautions.empty:
                    # Get all precaution columns that exist and have values
                    for i in range(1, 5):
                        col_name = f'Precaution{i}'
                        if col_name in disease_precautions.columns:
                            prec_value = disease_precautions[col_name].iloc[0]
                            if pd.notna(prec_value) and str(prec_value).strip():
                                precautions.append(str(prec_value).strip())
        except Exception as e:
            print(f"Error getting precautions: {e}")
            precautions = []
        
        # If no precautions found, add generic precautions
        if not precautions:
            precautions = [
                "Consult a healthcare professional immediately",
                "Get proper medical diagnosis",
                "Follow doctor's recommendations carefully",
                "Monitor symptoms and seek emergency care if they worsen"
            ]
        
        # Get nearby hospitals based on severity
        nearby_hospitals = []
        if hospital_data_available:
            try:
                nearby_hospitals = get_hospitals_by_severity(severity)
            except Exception as e:
                print(f"Error getting hospitals: {e}")
                nearby_hospitals = []
        
        # Store prediction in database
        prediction_record = Prediction(
            user_id=current_user.id,
            symptoms=json.dumps(selected_symptoms),
            predicted_disease=disease_name,
            confidence=confidence,
            severity=severity
        )
        db.session.add(prediction_record)
        db.session.commit()
        
        # Store in session for quick access
        session['last_prediction'] = {
            'disease': disease_name,
            'severity': severity,
            'confidence': confidence,
            'symptoms': selected_symptoms
        }
        
        return render_template('result.html',
                             disease=disease_name,
                             severity=severity,
                             selected_symptoms=selected_symptoms,
                             precautions=precautions,
                             nearby_hospitals=nearby_hospitals,
                             confidence=round(confidence, 2))
    
    except Exception as e:
        flash(f"Error making prediction: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

@app.route('/get_hospitals', methods=['GET'])
@login_required
def get_hospitals():
    """API endpoint to get nearby hospitals (for AJAX calls)"""
    try:
        if hospital_data_available:
            hospitals = get_all_hospitals()
            return jsonify({'success': True, 'hospitals': hospitals})
        else:
            return jsonify({'success': False, 'error': 'Hospital data not available'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    return jsonify({'symptoms': all_symptoms})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/profile')
@login_required
def profile():
    # Get prediction statistics
    total_predictions = Prediction.query.filter_by(user_id=current_user.id).count()
    
    # Get most common predicted disease
    from sqlalchemy import func
    common_disease = db.session.query(
        Prediction.predicted_disease,
        func.count(Prediction.id).label('count')
    ).filter_by(user_id=current_user.id)\
     .group_by(Prediction.predicted_disease)\
     .order_by(func.count(Prediction.id).desc())\
     .first()
    
    return render_template('profile.html',
                         user=current_user,
                         total_predictions=total_predictions,
                         common_disease=common_disease)

@app.route('/history')
@login_required
def history():
    page = request.args.get('page', 1, type=int)
    predictions = Prediction.query.filter_by(user_id=current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('history.html', predictions=predictions)
    

@app.route('/emergency_contacts')
@login_required
def emergency_contacts():
    """Emergency contacts page"""
    emergency_numbers = [
        {'name': 'Emergency Services', 'number': '911', 'description': 'Police, Fire, Ambulance'},
        {'name': 'Poison Control', 'number': '1-800-222-1222', 'description': '24/7 Poison Help'},
        {'name': 'Suicide Prevention', 'number': '988', 'description': 'Suicide & Crisis Lifeline'},
        {'name': 'Mental Health Crisis', 'number': '1-800-273-TALK', 'description': 'National Helpline'},
        {'name': 'Domestic Violence', 'number': '1-800-799-SAFE', 'description': 'National Hotline'},
        {'name': 'Child Abuse', 'number': '1-800-4-A-CHILD', 'description': 'Childhelp National Hotline'},
    ]
    
    return render_template('emergency_contacts.html', 
                         emergency_numbers=emergency_numbers,
                         user=current_user)

if __name__ == '__main__':
    print("✓ Hospital data loaded successfully")
    print("✓ Starting Flask application...")
    app.run(debug=True, port=5000)