"""
Safe Route AI System - Main Integration Module
Combines predictive safety scoring, dynamic geofencing, and Sakha chatbot
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import numpy as np

# Import our custom modules
from predictive_safety_model import PredictiveSafetyModel
from dynamic_geofencing import DynamicGeofencing, AlertPhase
from enhanced_route_optimizer import EnhancedRouteOptimizer, OptimizedRoute
from sakha_chatbot import SakhaChatbot, ChatbotState

class SafeRouteAISystem:
    def __init__(self, google_maps_api_key: str = None):
        """Initialize the complete Safe Route AI System"""
        # Initialize core components
        self.safety_model = PredictiveSafetyModel()
        self.geofencing = DynamicGeofencing(self.safety_model)
        self.route_optimizer = EnhancedRouteOptimizer(
            self.safety_model, google_maps_api_key
        )
        self.sakha_chatbot = SakhaChatbot()
        
        # System state
        self.active_routes = {}
        self.user_sessions = {}
        self.emergency_contacts = {}
        
        # Load and train the safety model
        self._initialize_safety_model()
    
    def _initialize_safety_model(self):
        """Initialize and train the safety model"""
        print("Initializing safety model...")
        
        # Try to load existing model
        if not self.safety_model.load_model():
            print("Training new safety model...")
            self.safety_model.train_model()
        
        print("Safety model ready!")
    
    def plan_safe_route(self, 
                       start_lat: float, 
                       start_lng: float,
                       end_lat: float, 
                       end_lng: float,
                       user_id: str,
                       departure_time: Optional[datetime] = None) -> Dict:
        """Plan an optimized safe route for a user"""
        if departure_time is None:
            departure_time = datetime.now()
        
        print(f"Planning safe route for user {user_id}...")
        
        # Get optimized route with safety scoring
        optimized_route = self.route_optimizer.optimize_route_with_safety_scoring(
            start_lat, start_lng, end_lat, end_lng, departure_time
        )
        
        if not optimized_route:
            return {"error": "Unable to plan route"}
        
        # Set up geofencing for the route
        route_coordinates = [(point.lat, point.lng) for point in optimized_route.points]
        self.geofencing.set_planned_route(route_coordinates)
        
        # Store route information
        route_id = f"route_{user_id}_{int(datetime.now().timestamp())}"
        self.active_routes[route_id] = {
            "user_id": user_id,
            "route": optimized_route,
            "start_time": departure_time,
            "status": "active"
        }
        
        # Create user session
        self.user_sessions[user_id] = {
            "route_id": route_id,
            "current_location": None,
            "safety_status": "monitoring",
            "last_update": datetime.now()
        }
        
        # Prepare route response
        route_response = {
            "route_id": route_id,
            "total_safety_score": optimized_route.total_safety_score,
            "total_travel_time": optimized_route.total_travel_time,
            "route_confidence": optimized_route.route_confidence,
            "waypoints": [
                {
                    "lat": point.lat,
                    "lng": point.lng,
                    "safety_score": point.safety_score,
                    "estimated_time": point.estimated_travel_time
                }
                for point in optimized_route.points
            ],
            "safety_recommendations": self._generate_route_recommendations(optimized_route)
        }
        
        print(f"Route planned successfully. Safety Score: {optimized_route.total_safety_score:.2f}")
        return route_response
    
    def update_user_location(self, user_id: str, lat: float, lng: float, 
                           speed: float = 0.0, accuracy: float = 10.0) -> Dict:
        """Update user location and check for safety anomalies"""
        if user_id not in self.user_sessions:
            return {"error": "User session not found"}
        
        # Update geofencing system
        anomaly_detected = self.geofencing.update_user_location(lat, lng, speed, accuracy)
        
        # Update user session
        self.user_sessions[user_id].update({
            "current_location": {"lat": lat, "lng": lng},
            "last_update": datetime.now()
        })
        
        # Get current safety status
        safety_status = self.geofencing.get_current_safety_status()
        
        # Handle anomalies
        response = {"location_updated": True, "anomaly_detected": anomaly_detected}
        
        if anomaly_detected:
            # Get current route
            route_id = self.user_sessions[user_id]["route_id"]
            if route_id in self.active_routes:
                route = self.active_routes[route_id]["route"]
                
                # Get real-time safety updates
                safety_updates = self.route_optimizer.get_real_time_safety_updates(
                    route, (lat, lng)
                )
                
                # Activate Sakha chatbot based on alert level
                alert_level = self._determine_alert_level(safety_status, safety_updates)
                sakha_response = self.sakha_chatbot.activate_proactive_intervention(
                    alert_level, {"lat": lat, "lng": lng}, safety_updates["current_safety_score"]
                )
                
                response.update({
                    "safety_updates": safety_updates,
                    "sakha_intervention": sakha_response,
                    "alert_level": alert_level
                })
        
        return response
    
    def _determine_alert_level(self, safety_status: Dict, safety_updates: Dict) -> int:
        """Determine alert level based on safety status and updates"""
        current_score = safety_updates.get("current_safety_score", 50)
        stopped_duration = safety_status.get("stopped_duration", 0)
        
        # Emergency level (3)
        if current_score < 20 or stopped_duration > 10:
            return 3
        
        # Escalation level (2)
        elif current_score < 40 or stopped_duration > 5:
            return 2
        
        # Soft check level (1)
        elif current_score < 60 or stopped_duration > 2:
            return 1
        
        # Normal level (0)
        else:
            return 0
    
    def _generate_route_recommendations(self, route: OptimizedRoute) -> List[str]:
        """Generate safety recommendations for the route"""
        recommendations = []
        
        # Analyze route safety scores
        safety_scores = [point.safety_score for point in route.points]
        avg_safety = np.mean(safety_scores)
        min_safety = np.min(safety_scores)
        
        if min_safety < 30:
            recommendations.append("Route contains high-risk areas - stay alert")
        
        if avg_safety < 50:
            recommendations.append("Overall route has moderate safety concerns")
        
        if route.route_confidence < 0.7:
            recommendations.append("Route safety predictions have lower confidence")
        
        # Time-based recommendations
        current_hour = datetime.now().hour
        if 22 <= current_hour or current_hour <= 5:
            recommendations.append("Night travel - ensure good lighting and company")
        
        return recommendations
    
    def process_sakha_message(self, user_id: str, message: str) -> Dict:
        """Process message to Sakha chatbot"""
        if user_id not in self.user_sessions:
            return {"error": "User session not found"}
        
        # Process message through Sakha
        sakha_response = self.sakha_chatbot.process_user_message(message, user_id)
        
        # Update user session
        self.user_sessions[user_id]["last_sakha_interaction"] = datetime.now()
        
        return sakha_response
    
    def get_user_safety_status(self, user_id: str) -> Dict:
        """Get comprehensive safety status for a user"""
        if user_id not in self.user_sessions:
            return {"error": "User session not found"}
        
        user_session = self.user_sessions[user_id]
        route_id = user_session["route_id"]
        
        if route_id not in self.active_routes:
            return {"error": "Active route not found"}
        
        # Get current safety status from geofencing
        safety_status = self.geofencing.get_current_safety_status()
        
        # Get Sakha conversation summary
        sakha_summary = self.sakha_chatbot.get_conversation_summary()
        
        # Get route information
        route_info = self.active_routes[route_id]
        
        return {
            "user_id": user_id,
            "current_location": user_session["current_location"],
            "safety_status": safety_status,
            "route_info": {
                "route_id": route_id,
                "total_safety_score": route_info["route"].total_safety_score,
                "route_confidence": route_info["route"].route_confidence
            },
            "sakha_status": {
                "state": self.sakha_chatbot.state.value,
                "alert_level": self.sakha_chatbot.current_alert_level,
                "conversation_summary": sakha_summary
            },
            "last_update": user_session["last_update"].isoformat()
        }
    
    def set_emergency_contacts(self, user_id: str, contacts: List[Dict]):
        """Set emergency contacts for a user"""
        self.emergency_contacts[user_id] = contacts
        self.sakha_chatbot.set_emergency_contacts(contacts)
        
        return {"status": "emergency_contacts_set", "count": len(contacts)}
    
    def end_user_session(self, user_id: str) -> Dict:
        """End user session and cleanup"""
        if user_id not in self.user_sessions:
            return {"error": "User session not found"}
        
        # Get route ID
        route_id = self.user_sessions[user_id]["route_id"]
        
        # Mark route as completed
        if route_id in self.active_routes:
            self.active_routes[route_id]["status"] = "completed"
        
        # Reset Sakha chatbot
        self.sakha_chatbot.reset_state()
        
        # Remove user session
        del self.user_sessions[user_id]
        
        return {"status": "session_ended", "user_id": user_id}
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        return {
            "active_routes": len([r for r in self.active_routes.values() if r["status"] == "active"]),
            "active_users": len(self.user_sessions),
            "safety_model_loaded": self.safety_model.model is not None,
            "sakha_state": self.sakha_chatbot.state.value,
            "system_uptime": datetime.now().isoformat()
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the complete system
    safe_route_ai = SafeRouteAISystem()
    
    # Test user session
    user_id = "test_user_001"
    start_lat, start_lng = 28.6139, 77.2090  # Delhi
    end_lat, end_lng = 28.6169, 77.2120
    
    print("=== Safe Route AI System Test ===")
    
    # 1. Plan a safe route
    print("\n1. Planning safe route...")
    route_response = safe_route_ai.plan_safe_route(
        start_lat, start_lng, end_lat, end_lng, user_id
    )
    print(f"Route planned: {route_response.get('route_id', 'Failed')}")
    print(f"Safety Score: {route_response.get('total_safety_score', 'N/A')}")
    
    # 2. Set emergency contacts
    print("\n2. Setting emergency contacts...")
    emergency_contacts = [
        {"name": "Emergency Contact 1", "phone": "+91-9876543210"},
        {"name": "Emergency Contact 2", "phone": "+91-9876543211"}
    ]
    safe_route_ai.set_emergency_contacts(user_id, emergency_contacts)
    
    # 3. Simulate user movement
    print("\n3. Simulating user movement...")
    test_locations = [
        (28.6149, 77.2100, 0.0),  # Stopped
        (28.6159, 77.2110, 0.0),  # Stopped
        (28.6169, 77.2120, 0.0),  # Stopped
    ]
    
    for i, (lat, lng, speed) in enumerate(test_locations):
        print(f"\nLocation {i+1}: ({lat}, {lng})")
        location_response = safe_route_ai.update_user_location(user_id, lat, lng, speed)
        print(f"Anomaly detected: {location_response.get('anomaly_detected', False)}")
        
        if location_response.get('sakha_intervention'):
            print("Sakha intervention activated!")
    
    # 4. Test Sakha chatbot
    print("\n4. Testing Sakha chatbot...")
    sakha_response = safe_route_ai.process_sakha_message(user_id, "I'm feeling unsafe")
    print(f"Sakha response: {sakha_response.get('message', 'No response')}")
    
    # 5. Get safety status
    print("\n5. Getting safety status...")
    safety_status = safe_route_ai.get_user_safety_status(user_id)
    print(f"Safety status: {safety_status.get('safety_status', {})}")
    
    # 6. End session
    print("\n6. Ending user session...")
    end_response = safe_route_ai.end_user_session(user_id)
    print(f"Session ended: {end_response.get('status', 'Failed')}")
    
    # 7. System status
    print("\n7. System status...")
    system_status = safe_route_ai.get_system_status()
    print(f"System status: {system_status}")
    
    print("\n=== Test Complete ===")
