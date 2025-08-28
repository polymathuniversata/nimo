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
            "GET /api/health - Health check",
            "GET /api/contributions - Get contributions",
            "GET /api/bonds - Get bonds",
            "GET /api/tokens/balance - Get token balance",
            "POST /api/contributions/verify - Verify contribution with MeTTa"
        ]
    }), 200

# Frontend API endpoints for demo
@app.route('/api/contributions', methods=['GET'])
def get_contributions():
    """Mock endpoint for contributions"""
    return jsonify({
        "contributions": [
            {
                "id": 1,
                "title": "Sample AI Research Contribution",
                "description": "Research on advanced MeTTa reasoning systems for blockchain verification",
                "contribution_type": "research",
                "impact_level": "significant",
                "created_at": "2024-02-20T10:30:00Z",
                "user_id": 1,
                "wallet_address": "0x1234567890123456789012345678901234567890",
                "evidence": {"type": "link", "url": "https://github.com/sample/research"},
                "verifications": [
                    {
                        "id": 1,
                        "verifier_name": "MeTTa AI System",
                        "organization": "Automated Verification",
                        "comments": "AI-verified research with significant impact on hypergraph reasoning",
                        "confidence": 0.92,
                        "created_at": "2024-02-20T11:00:00Z"
                    }
                ],
                "metta_processing": False,
                "metta_confidence": 0.92,
                "metta_reasoning": "High-quality research contribution with novel insights"
            }
        ]
    }), 200

@app.route('/api/bonds', methods=['GET'])
def get_bonds():
    """Mock endpoint for impact bonds"""
    return jsonify([
        {
            "id": 1,
            "title": "Carbon Reduction Initiative",
            "description": "Blockchain-verified carbon offset program with AI monitoring",
            "target_amount": 100000,
            "current_amount": 75000,
            "token_price": 25.50,
            "apy": 8.5,
            "maturity_date": "2025-12-31",
            "impact_metrics": {
                "co2_reduced": 1250,
                "target_co2": 2000
            },
            "verification_status": "verified",
            "milestones": []
        }
    ]), 200

@app.route('/api/tokens/balance', methods=['GET'])
def get_token_balance():
    """Mock endpoint for token balance"""
    return jsonify({
        "balance": 1250.75,
        "updated_at": "2024-02-20T15:30:00Z"
    }), 200

@app.route('/api/contributions/verify', methods=['POST'])
def verify_contribution():
    """Mock endpoint for MeTTa contribution verification"""
    from flask import request
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Mock MeTTa verification logic
        impact_level = data.get('impact_level', 'low')
        
        # Simulate verification confidence based on impact level
        confidence_map = {
            'transformative': 0.95,
            'significant': 0.88,
            'moderate': 0.75,
            'low': 0.65
        }
        
        confidence = confidence_map.get(impact_level, 0.70)
        verified = confidence > 0.70
        
        reasoning = f"AI analysis indicates {impact_level} impact with {confidence:.1%} confidence. " + \
                   "Contribution shows clear evidence of positive community impact and technical merit."
        
        return jsonify({
            "verified": verified,
            "confidence": confidence,
            "reasoning": reasoning,
            "metta_analysis": {
                "technical_merit": confidence,
                "community_impact": confidence * 0.9,
                "evidence_quality": confidence * 1.1 if confidence * 1.1 <= 1.0 else 1.0
            }
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)