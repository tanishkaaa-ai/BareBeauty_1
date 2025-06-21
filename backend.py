from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai
import json
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for your frontend

# Set up the Gemini API client
API_KEY = "AIzaSyDNlC8p5OUoCbO7ALzO8GJLX99lWMFoVN0"  # Store your API key as an environment variable

import requests

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
    
    # Convert budget code to readable text
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
    # This is a simplified parser - you may need to refine based on actual responses
    recommendations = []
    
    # Split text by numbered items (1., 2., etc.) or product names
    sections = text.split("\n\n")
    current_product = {}
    
    for section in sections:
        if not section.strip():
            continue
            
        # Check if this is a new product section
        if section.strip().startswith(("1.", "2.", "3.", "4.", "5.")) or "Product" in section:
            # Save the previous product if it exists
            if current_product and 'name' in current_product:
                recommendations.append(current_product)
                current_product = {}
            
            # Extract product details
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
    
    # Add the last product if it exists
    if current_product and 'name' in current_product:
        recommendations.append(current_product)
    
    return recommendations

@app.route('/')
def home():
    return "Flask backend is running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)