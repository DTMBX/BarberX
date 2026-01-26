"""
Minimal BarberX App for Deployment Diagnosis
This is a stripped-down version to identify what's breaking
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')

# Enable CORS
CORS(app)

# Simple routes to test deployment
@app.route('/')
def index():
    """Minimal homepage"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BarberX Legal Technologies</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .card {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c3e50; }
            .status { color: #27ae60; font-weight: bold; }
            a {
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 10px 20px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            a:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎉 BarberX Legal Technologies</h1>
            <p class="status">✅ App is running successfully!</p>
            <p>Professional BWC Forensic Analysis Platform</p>
            
            <h2>Test Endpoints:</h2>
            <a href="/health">Health Check</a>
            <a href="/api/test">API Test</a>
            <a href="/env">Environment Info</a>
            
            <h2>System Status:</h2>
            <ul>
                <li>Server: Flask (Python)</li>
                <li>Status: Online</li>
                <li>Time: {{ now }}</li>
            </ul>
        </div>
    </body>
    </html>
    ''', now=datetime.utcnow().isoformat())

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'app': 'BarberX Legal Technologies',
        'version': '2.0-minimal'
    })

@app.route('/api/test')
def api_test():
    """Test API endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is working!',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/env')
def env_info():
    """Show environment info (safe subset)"""
    return jsonify({
        'python_version': os.sys.version,
        'flask_env': os.getenv('FLASK_ENV', 'not set'),
        'port': os.getenv('PORT', 'not set'),
        'has_database_url': 'Yes' if os.getenv('DATABASE_URL') else 'No',
        'has_secret_key': 'Yes' if os.getenv('SECRET_KEY') else 'No (using default)'
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested URL was not found',
        'available_routes': [
            '/',
            '/health',
            '/api/test',
            '/env'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(e),
        'timestamp': datetime.utcnow().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
