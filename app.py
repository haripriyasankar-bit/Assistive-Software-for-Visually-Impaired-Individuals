from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Set up OpenAI configuration (using OpenRouter)
openai.api_key = os.getenv('OPENAI_API_KEY')
openai.api_base = "https://openrouter.ai/api/v1"

@app.route('/')
def home():
    """Render the chatbot home page"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests and return AI responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if not openai.api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Create conversation with OpenAI using ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        return jsonify({
            'response': ai_response,
            'status': 'success'
        })
        
    except Exception as e:
        # Handle OpenAI API errors
        error_message = str(e)
        if "AuthenticationError" in error_message or "Invalid API key" in error_message:
            return jsonify({'error': 'Invalid OpenAI API key'}), 401
        elif "RateLimitError" in error_message or "rate limit" in error_message.lower():
            return jsonify({'error': 'API rate limit exceeded. Please try again later.'}), 429
        elif "API" in error_message:
            return jsonify({'error': f'OpenAI API error: {error_message}'}), 500
        else:
            return jsonify({'error': f'Internal server error: {error_message}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Chatbot API is running'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
