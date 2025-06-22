from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from flask_login import LoginManager
import os
import google.generativeai as genai
import json
import requests
from werkzeug.security import generate_password_hash, check_password_hash

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

login_manager = LoginManager()

# JWT Secret Key (should be an environment variable in production)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

# In-memory user "database" for demo
users = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class QuizResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'))
    data = db.Column(db.Text)  # JSON string

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

login_manager = LoginManager()

# JWT Secret Key (should be an environment variable in production)
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)

# In-memory user "database" for demo
users = {}

# Set up the Gemini API client
API_KEY = "AIzaSyDNlC8p5OUoCbO7ALzO8GJLX99lWMFoVN0"  # Store your API key as an environment variable

@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400
    if email in users:
        return jsonify({'error': 'User already exists'}), 400

    users[email] = {
        'name': name,
        'email': email,
        'password': generate_password_hash(password)
    }
    return jsonify({'message': 'User created!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    user = users.get(email)
    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=email)
    return jsonify({'access_token': access_token, 'user': {'name': user['name'], 'email': user['email']}}), 200

# Example of a protected endpoint
@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({'logged_in_as': current_user}), 200

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    quiz_results = data.get('quizResults')
    recommendation_type = data.get('type')

    prompt = create_prompt(quiz_results, recommendation_type)

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        headers = { "Content-Type": "application/json" }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        response_text = result['candidates'][0]['content']['parts'][0]['text']
        recommendations = process_response(response_text, recommendation_type)

        return jsonify({"recommendations": recommendations})
    except Exception as e:
        print("Error calling Gemini API:", e)
        return jsonify({"error": str(e)}), 500

def create_prompt(quiz_results, recommendation_type):
    """Create a prompt for Gemini based on quiz results"""
    skin_type = quiz_results.get('skinType', 'Not specified')
    skin_concerns = quiz_results.get('skinConcerns', [])
    skin_tone = quiz_results.get('skinTone', 'Not specified')
    budget = quiz_results.get('budget', 'mid')
    budget_text = {
        'low': 'Below ₹500',
        'mid': '₹500 to ₹1500',
        'high': '₹1500 to ₹5000',
        'luxury': '₹5000+'
    }.get(budget, 'Not specified')
    preferred_brands = quiz_results.get('preferredBrands', [])
    brands_text = ', '.join(preferred_brands) if preferred_brands else 'No specific preference'
    if recommendation_type == 'skincare':
        prompt = f"""
        Act as a skincare expert. Recommend 5 skincare products for a person with the following profile:
        - Skin Type: {skin_type}
        - Skin Concerns: {', '.join(skin_concerns)}
        - Skin Tone: {skin_tone}
        - Budget: {budget_text}
        - Preferred Brands: {brands_text}

        For each product, provide:
        1. Product name
        2. Brand
        3. Price range in ₹ (Indian Rupees)
        4. Brief description
        5. Why it's specifically recommended for this user

        Format each product recommendation with clear headings and provide specific products that address the user's skin concerns.
        """
    else:  # makeup
        makeup_style = quiz_results.get('makeupProducts', [])
        prompt = f"""
        Act as a makeup expert. Recommend 5 makeup products for a person with the following profile:
        - Skin Type: {skin_type}
        - Skin Concerns: {', '.join(skin_concerns)}
        - Skin Tone: {skin_tone}
        - Makeup Style Preferences: {', '.join(makeup_style)}
        - Budget: {budget_text}
        - Preferred Brands: {brands_text}

        For each product, provide:
        1. Product name
        2. Brand
        3. Price range in ₹ (Indian Rupees)
        4. Brief description
        5. Why it's specifically recommended for this user

        Format each product recommendation with clear headings and provide specific products that match the user's makeup style preferences.
        """
    return prompt

def process_response(text, recommendation_type):
    """Process the Gemini response into structured data"""
    recommendations = []
    sections = text.split("\n\n")
    current_product = {}
    for section in sections:
        if not section.strip():
            continue
        if section.strip().startswith(("1.", "2.", "3.", "4.", "5.")) or "Product" in section:
            if current_product and 'name' in current_product:
                recommendations.append(current_product)
                current_product = {}
            lines = section.strip().split("\n")
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().lower()
                    value = value.strip()
                    if "product" in key or "name" in key:
                        current_product['name'] = value
                    elif "brand" in key:
                        current_product['brand'] = value
                    elif "price" in key:
                        current_product['price'] = value
                    elif "description" in key:
                        current_product['description'] = value
                    elif "why" in key and "recommended" in key:
                        current_product['whyRecommended'] = value
    if current_product and 'name' in current_product:
        recommendations.append(current_product)
    return recommendations

@app.route('/')
def home():
    return "Flask backend is running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)