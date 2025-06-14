from flask import Flask, render_template_string
from flask_cors import CORS

from client.es_client import load_mappings
from routes.translate_route import bp as translate_bp

DOCS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>WebCammerPlus API Documentation</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { background: #007bff; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
        .method.POST { background: #28a745; }
        .service { background: #e9ecef; padding: 15px; margin: 10px 0; border-radius: 5px; }
        code { background: #f8f9fa; padding: 2px 5px; border-radius: 3px; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>WebCammerPlus API Documentation</h1>
    
    <h2>Overview</h2>
    <p>This API provides translation, text generation, and reply services powered by Novita AI.</p>
    
    <h2>API Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method POST">POST</span> /translate/</h3>
        <p>Translates text from one language to another using AI translation services.</p>
        
        <h4>Request Body:</h4>
        <pre>{
  "text": "Hello world",           // Required: Text to translate
  "to_lang": "es",            // Required: Target language code
  "from_lang": "en"           // Optional: Source language code (auto-detect if not provided)
}</pre>
        
        <h4>Response:</h4>
        <pre>{
  "success": true,
  "translation": "Hola mundo"
}</pre>
        
        <h4>Error Response (400):</h4>
        <pre>{
  "error": "Both 'text' and 'to_lang' fields are required."
}</pre>
    </div>
    
    <h2>Available Services</h2>
    
    <div class="service">
        <h3>Translation Service</h3>
        <p><code>services.translate_service.translate_text(text, to_lang, from_lang=None)</code></p>
        <p>Core translation functionality using AI models to translate text between languages.</p>
        <ul>
            <li><strong>text</strong>: Source text to translate</li>
            <li><strong>to_lang</strong>: Target language code (e.g., 'es', 'fr', 'de')</li>
            <li><strong>from_lang</strong>: Optional source language code (auto-detected if not provided)</li>
        </ul>
    </div>
    
    <div class="service">
        <h3>Reply Service</h3>
        <p><code>services.reply_service.reply_text(original_text, response_idea, style, to_lang)</code></p>
        <p>Generates AI-powered replies to messages with specified style and language.</p>
        <ul>
            <li><strong>original_text</strong>: The original message to reply to</li>
            <li><strong>response_idea</strong>: General idea or direction for the response</li>
            <li><strong>style</strong>: Writing style (e.g., 'formal', 'casual', 'professional')</li>
            <li><strong>to_lang</strong>: Target language for the reply</li>
        </ul>
    </div>
    
    <div class="service">
        <h3>Write Service</h3>
        <p><code>services.write_service.write_text(style, text, to_lang)</code></p>
        <p>Generates written content about a given topic with specified style and language.</p>
        <ul>
            <li><strong>style</strong>: Writing style (e.g., 'formal', 'creative', 'technical')</li>
            <li><strong>text</strong>: Topic or subject to write about</li>
            <li><strong>to_lang</strong>: Target language for the generated content</li>
        </ul>
    </div>
    
    <h2>Technical Details</h2>
    
    <h3>AI Model Configuration</h3>
    <ul>
        <li><strong>Model:</strong> meta-llama/llama-3.2-3b-instruct</li>
        <li><strong>Provider:</strong> Novita AI</li>
        <li><strong>API Endpoint:</strong> https://api.novita.ai/v3/openai/chat/completions</li>
        <li><strong>Authentication:</strong> Bearer token via NOVITA_API_KEY environment variable</li>
    </ul>
    
    <h3>Data Storage</h3>
    <p>The application uses Elasticsearch for data persistence with the following mappings:</p>
    <ul>
        <li><code>mapping/account.json</code> - User account data structure</li>
        <li><code>mapping/subscription.json</code> - Subscription information</li>
        <li><code>mapping/token.json</code> - Authentication token storage</li>
    </ul>
    
    <h3>Error Handling</h3>
    <p>All endpoints return appropriate HTTP status codes:</p>
    <ul>
        <li><strong>200:</strong> Success</li>
        <li><strong>400:</strong> Bad Request (missing required fields or invalid data)</li>
        <li><strong>500:</strong> Internal Server Error</li>
    </ul>
    
    <h2>Development</h2>
    <p>To run the server in development mode:</p>
    <pre>cd server/
python app.py</pre>
    
    <p>The server will start on <code>http://localhost:5000</code> with debug mode enabled.</p>
    
    <h2>Testing</h2>
    <p>Run tests using pytest:</p>
    <pre>pytest</pre>
    
    <p>Test files are located alongside their corresponding service files with <code>_test.py</code> suffix.</p>
</body>
</html>
"""


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    load_mappings()
    
    @app.route("/")
    def docs():
        return render_template_string(DOCS_TEMPLATE)
    
    app.register_blueprint(translate_bp, url_prefix="/translate")
    return app


if __name__ == "__main__":
    # cd into server/ and run:
    create_app().run(debug=True)  # nosec B201 - Development only
