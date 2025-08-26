from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/api/health')
def health_check():
    return {"status": "ok"}, 200

if __name__ == '__main__':
    app.run(debug=True)