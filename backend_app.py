# backend_app.py
import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- SECURELY LOAD YOUR GEMINI API KEY ---
# Correctly get the environment variable named "GEMINI_API_KEY"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables or .env file.")
    print("Please ensure you have a .env file in the 'backend' directory")
    print("with a line like: GEMINI_API_KEY='YOUR_ACTUAL_GEMINI_API_KEY_HERE'")
    # For development, you might continue, but for production, you should
    # raise ValueError("GEMINI_API_KEY environment variable not set.")

# Gemini API Endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

app = Flask(__name__)
# Configure CORS to allow requests from your React app (running on default port 3000)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

def call_gemini_for_ideas(niche, successful_content_types, platform_type):
    """
    Function to make the actual API call to Gemini.
    This function contains the sensitive API key and runs on the backend.
    """
    if not GEMINI_API_KEY:
        return "Error: Gemini API key is not set in backend environment.", 500

    # Define the prompt for the Gemini model
    prompt = f"""
You are an expert social media content strategist.
Given the niche '{niche}' and recent successful content types '{successful_content_types}',
generate 5 unique and engaging content ideas for a {platform_type}.
Provide a catchy title for each idea and a brief description.

Format your output like this:
Idea 1: [Catchy Title]
Description: [Brief description of the content idea]

Idea 2: [Catchy Title]
Description: [Brief description of the content idea]

...and so on for 5 ideas.
"""

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": 0.8,
            "maxOutputTokens": 500
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        # Make the POST request to the Gemini API using the SECURE_GEMINI_API_KEY
        response = requests.post(f"{GEMINI_API_URL}?key={GEMINI_API_KEY}", headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        response_data = response.json()

        if response_data and response_data.get("candidates"):
            return response_data["candidates"][0]["content"]["parts"][0]["text"], 200
        else:
            return "Gemini API did not return expected content.", 500

    except requests.exceptions.RequestException as e:
        return f"Backend API Error: Failed to connect to Gemini: {e}", 500
    except KeyError:
        return "Backend API Error: Unexpected Gemini response format.", 500
    except json.JSONDecodeError:
        return "Backend API Error: Could not decode Gemini response.", 500
    except Exception as e:
        return f"Backend API Error: An unexpected error occurred: {e}", 500

@app.route('/api/generate_ideas', methods=['POST'])
def generate_ideas_endpoint():
    # Ensure the request body is JSON
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.json
    niche = data.get('niche', '')
    successful_content_types = data.get('successful_content_types', '')
    platform_type = data.get('platform_type', '')

    if not niche or not platform_type:
        return jsonify({"error": "Missing required parameters (niche, platform_type)"}), 400

    # Call the function that interacts with Gemini
    ideas, status_code = call_gemini_for_ideas(niche, successful_content_types, platform_type)

    if status_code != 200:
        return jsonify({"error": ideas}), status_code
    else:
        return jsonify({"ideas": ideas})

if __name__ == '__main__':
    print("Starting Flask backend on http://127.0.0.1:5000")
    print("Ensure your Gemini API Key is set in a .env file or environment variable.")
    # Set use_reloader=False if you want to explicitly control reloading,
    # but debug=True implies reloading, and it's generally fine for dev.
    app.run(debug=True, port=5000)