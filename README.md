# AI Chatbot - ChatGPT Style Web Application

A complete ChatGPT-like chatbot web application built with Flask backend and modern frontend, featuring OpenAI API integration for intelligent conversations.

## Features

- **Modern ChatGPT-style UI** - Clean, responsive interface similar to ChatGPT
- **Real-time AI Responses** - Powered by OpenAI GPT models
- **Chat History Persistence** - Messages saved in browser storage
- **Responsive Design** - Works perfectly on desktop and mobile devices
- **Loading Animations** - Visual feedback while AI is thinking
- **Error Handling** - Comprehensive error management with user-friendly messages
- **Character Counter** - Track message length with visual indicators
- **Keyboard Shortcuts** - Enter to send, Shift+Enter for new line
- **Clear Chat Function** - Reset conversation with confirmation
- **Auto-scroll** - Automatically scroll to latest messages
- **Status Indicators** - Show online status and connection state

## Project Structure

```
chatbot/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (API key)
├── README.md             # This file
├── templates/
│   └── index.html        # Main HTML template
└── static/
    ├── css/
    │   └── style.css     # Complete styling
    └── js/
        └── script.js      # Frontend JavaScript
```

## Setup Instructions

### Prerequisites
- Python 3.7 or higher
- OpenAI API key (get one from [platform.openai.com](https://platform.openai.com/))

### Installation Steps

1. **Clone or download the project**
   ```bash
   # If using git
   git clone <repository-url>
   cd chatbot
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure OpenAI API Key**
   - Open the `.env` file
   - Replace `your_openai_api_key_here` with your actual OpenAI API key
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the chatbot**
   - Open your web browser
   - Go to `http://localhost:5000`
   - Start chatting!

## Usage

1. **Sending Messages**
   - Type your message in the input box
   - Press Enter or click the send button
   - Use Shift+Enter for new lines

2. **Chat Features**
   - **Clear Chat**: Click the trash icon to reset conversation
   - **Chat History**: Messages persist until browser refresh or manual clear
   - **Character Limit**: 2000 characters per message with visual indicator
   - **Auto-scroll**: Chat automatically scrolls to latest messages

3. **Keyboard Shortcuts**
   - `Enter`: Send message
   - `Shift + Enter`: New line
   - `Ctrl/Cmd + K`: Clear chat
   - `Escape`: Focus input field

## API Endpoints

### `GET /`
- Renders the main chatbot interface

### `POST /chat`
- Handles chat messages and returns AI responses
- **Request Body**: `{"message": "your message here"}`
- **Response**: `{"response": "AI response", "status": "success"}`
- **Error Response**: `{"error": "error message"}`

### `GET /health`
- Health check endpoint
- **Response**: `{"status": "healthy", "message": "Chatbot API is running"}`

## Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Customization Options
You can modify the following in the code:
- **AI Model**: Change `gpt-3.5-turbo` in `app.py` to other OpenAI models
- **Max Tokens**: Adjust response length limit
- **Temperature**: Control AI creativity (0.0-1.0)
- **UI Colors**: Modify CSS variables in `style.css`
- **Port**: Change default port 5000 in `app.py`

## Error Handling

The application handles various error scenarios:
- Invalid or missing OpenAI API key
- API rate limits
- Network connectivity issues
- Empty message submissions
- Malformed request data

Error messages are displayed in a user-friendly toast notification.

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Security Features

- API key stored in environment variables (not exposed to frontend)
- CORS protection configured
- Input sanitization and validation
- Rate limiting awareness
- Secure headers implementation

## Performance Optimizations

- Lazy loading of chat history
- Efficient DOM manipulation
- Debounced input handling
- Optimized scroll behavior
- Minimal external dependencies

## Deployment Options

### Local Development
- Follow the setup instructions above
- Suitable for development and testing

### Production Deployment
Consider using:
- **Gunicorn** or **uWSGI** as WSGI server
- **Nginx** as reverse proxy
- **Environment variables** for configuration
- **HTTPS** for secure connections

Example production command:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

### Common Issues

1. **"Invalid OpenAI API key"**
   - Verify your API key is correct
   - Check if the key has credits
   - Ensure the key is properly set in `.env`

2. **"API rate limit exceeded"**
   - Wait and try again later
   - Check your OpenAI usage limits
   - Consider upgrading your plan

3. **"Connection refused"**
   - Ensure the Flask app is running
   - Check if port 5000 is available
   - Verify firewall settings

4. **Styling issues**
   - Clear browser cache
   - Check browser console for errors
   - Ensure static files are accessible

### Debug Mode
For development, you can enable debug mode in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## Contributing

Feel free to contribute improvements:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code comments
3. Open an issue in the repository

---

**Enjoy your AI chatbot! 🤖**
