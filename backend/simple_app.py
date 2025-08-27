from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "message": "Backend server is running"}), 200

@app.route('/')
def root():
    return jsonify({
        "message": "Nimo Platform API Server",
        "version": "1.0.0",
        "status": "operational"
    }), 200

@app.route('/api')
def api_info():
    return jsonify({
        "message": "Nimo Platform API",
        "version": "1.0.0",
        "available_endpoints": [
            "GET /api/health - Health check"
        ]
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')