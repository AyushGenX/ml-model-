"""
Enhanced API Server for Safe Route AI System
Integrates with existing Node.js backend and adds new AI-powered features
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import asyncio
from datetime import datetime
import os
import sys

# Add the pythonScript directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pythonScript'))

from safe_route_ai_system import SafeRouteAISystem
from sakha_chatbot import ChatbotState

app = Flask(__name__)
CORS(app)

# Initialize the AI system
safe_route_ai = SafeRouteAISystem()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system_status": safe_route_ai.get_system_status()
    })

@app.route('/api/plan-safe-route', methods=['POST'])
def plan_safe_route():
    """Plan an AI-optimized safe route"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['source', 'destination', 'user_id']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        source = data['source']
        destination = data['destination']
        user_id = data['user_id']
        
        # Optional fields
        departure_time = data.get('departure_time')
        if departure_time:
            departure_time = datetime.fromisoformat(departure_time)
        
        # Plan the route
        route_response = safe_route_ai.plan_safe_route(
            start_lat=source['lat'],
            start_lng=source['lng'],
            end_lat=destination['lat'],
            end_lng=destination['lng'],
            user_id=user_id,
            departure_time=departure_time
        )
        
        if 'error' in route_response:
            return jsonify(route_response), 500
        
        return jsonify({
            "success": True,
            "data": route_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/update-location', methods=['POST'])
def update_location():
    """Update user location and get safety status"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = data['user_id']
        location = data['location']
        speed = data.get('speed', 0.0)
        accuracy = data.get('accuracy', 10.0)
        
        # Update location
        location_response = safe_route_ai.update_user_location(
            user_id=user_id,
            lat=location['lat'],
            lng=location['lng'],
            speed=speed,
            accuracy=accuracy
        )
        
        return jsonify({
            "success": True,
            "data": location_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sakha-chat', methods=['POST'])
def sakha_chat():
    """Chat with Sakha safety assistant"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data or 'message' not in data:
            return jsonify({"error": "Missing required fields: user_id, message"}), 400
        
        user_id = data['user_id']
        message = data['message']
        
        # Create user session if it doesn't exist
        if user_id not in safe_route_ai.user_sessions:
            safe_route_ai.user_sessions[user_id] = {
                "route_id": None,
                "current_location": None,
                "safety_status": "monitoring",
                "last_update": datetime.now(),
                "last_sakha_interaction": None
            }
        
        # Activate Sakha if not already active
        if safe_route_ai.sakha_chatbot.state.value == "idle":
            safe_route_ai.sakha_chatbot.state = ChatbotState.ACTIVE
        
        # Process message through Sakha
        sakha_response = safe_route_ai.process_sakha_message(user_id, message)
        
        return jsonify({
            "success": True,
            "data": sakha_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/safety-status/<user_id>', methods=['GET'])
def get_safety_status(user_id):
    """Get comprehensive safety status for a user"""
    try:
        safety_status = safe_route_ai.get_user_safety_status(user_id)
        
        if 'error' in safety_status:
            return jsonify(safety_status), 404
        
        return jsonify({
            "success": True,
            "data": safety_status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/emergency-contacts', methods=['POST'])
def set_emergency_contacts():
    """Set emergency contacts for a user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'user_id' not in data or 'contacts' not in data:
            return jsonify({"error": "Missing required fields: user_id, contacts"}), 400
        
        user_id = data['user_id']
        contacts = data['contacts']
        
        # Validate contacts format
        if not isinstance(contacts, list):
            return jsonify({"error": "Contacts must be a list"}), 400
        
        for contact in contacts:
            if not isinstance(contact, dict) or 'name' not in contact or 'phone' not in contact:
                return jsonify({"error": "Each contact must have 'name' and 'phone' fields"}), 400
        
        # Set emergency contacts
        contacts_response = safe_route_ai.set_emergency_contacts(user_id, contacts)
        
        return jsonify({
            "success": True,
            "data": contacts_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/end-session/<user_id>', methods=['POST'])
def end_session(user_id):
    """End user session"""
    try:
        end_response = safe_route_ai.end_user_session(user_id)
        
        if 'error' in end_response:
            return jsonify(end_response), 404
        
        return jsonify({
            "success": True,
            "data": end_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/predict-safety-score', methods=['POST'])
def predict_safety_score():
    """Predict safety score for a specific location and time"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'lat' not in data or 'lng' not in data:
            return jsonify({"error": "Missing required fields: lat, lng"}), 400
        
        lat = data['lat']
        lng = data['lng']
        timestamp = data.get('timestamp')
        
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp)
        
        # Predict safety score
        safety_score = safe_route_ai.safety_model.predict_safety_score(lat, lng, timestamp)
        
        return jsonify({
            "success": True,
            "data": {
                "lat": lat,
                "lng": lng,
                "safety_score": safety_score,
                "timestamp": datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    """Get overall system status"""
    try:
        system_status = safe_route_ai.get_system_status()
        
        return jsonify({
            "success": True,
            "data": system_status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    print("Starting Enhanced Safe Route AI API Server...")
    print("System Status:", safe_route_ai.get_system_status())
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
