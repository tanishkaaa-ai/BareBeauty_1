import requests
from backend import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

API_KEY = "1a92e8f9-58d2-4d64-50ac-cf796d03094a"
ANALYSIS_URL = "https://api.skinanalysis.com/analyze"  # replace with actual API endpoint

@app.route('/analyze', methods=['POST'])
def analyze():
    image = request.files['image']

    files = {'image': (image.filename, image.stream, image.content_type)}
    headers = {'Authorization': f'Bearer {API_KEY}'}  # or 'apikey': API_KEY if the service requires it that way

    response = requests.post(ANALYSIS_URL, headers=headers, files=files)

    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Failed to analyze'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)
