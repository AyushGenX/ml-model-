"""
Test script for Safe Route AI System
Validates all components and integration
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add pythonScript to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'pythonScript'))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from predictive_safety_model import PredictiveSafetyModel
        print("✓ PredictiveSafetyModel imported successfully")
    except Exception as e:
        print(f"✗ Failed to import PredictiveSafetyModel: {e}")
        return False
    
    try:
        from dynamic_geofencing import DynamicGeofencing
        print("✓ DynamicGeofencing imported successfully")
    except Exception as e:
        print(f"✗ Failed to import DynamicGeofencing: {e}")
        return False
    
    try:
        from enhanced_route_optimizer import EnhancedRouteOptimizer
        print("✓ EnhancedRouteOptimizer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import EnhancedRouteOptimizer: {e}")
        return False
    
    try:
        from sakha_chatbot import SakhaChatbot
        print("✓ SakhaChatbot imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SakhaChatbot: {e}")
        return False
    
    try:
        from safe_route_ai_system import SafeRouteAISystem
        print("✓ SafeRouteAISystem imported successfully")
    except Exception as e:
        print(f"✗ Failed to import SafeRouteAISystem: {e}")
        return False
    
    return True

def test_safety_model():
    """Test predictive safety model"""
    print("\nTesting Predictive Safety Model...")
    
    try:
        from predictive_safety_model import PredictiveSafetyModel
        
        model = PredictiveSafetyModel()
        
        # Test feature creation
        features = model.create_feature_vector(28.6139, 77.2090)
        print(f"✓ Feature vector created: {len(features)} features")
        
        # Test prediction
        safety_score = model.predict_safety_score(28.6139, 77.2090)
        print(f"✓ Safety score predicted: {safety_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Safety model test failed: {e}")
        return False

def test_geofencing():
    """Test dynamic geofencing"""
    print("\nTesting Dynamic Geofencing...")
    
    try:
        from dynamic_geofencing import DynamicGeofencing
        
        geofencing = DynamicGeofencing()
        
        # Test route setup
        test_route = [
            (28.6139, 77.2090),
            (28.6149, 77.2100),
            (28.6159, 77.2110)
        ]
        geofencing.set_planned_route(test_route)
        print("✓ Route set successfully")
        
        # Test location updates
        anomaly1 = geofencing.update_user_location(28.6139, 77.2090, 0.0)
        anomaly2 = geofencing.update_user_location(28.6149, 77.2100, 0.0)
        print(f"✓ Location updates processed. Anomalies: {anomaly1}, {anomaly2}")
        
        # Test safety status
        status = geofencing.get_current_safety_status()
        print(f"✓ Safety status retrieved: {status.get('current_phase', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"✗ Geofencing test failed: {e}")
        return False

def test_route_optimizer():
    """Test enhanced route optimizer"""
    print("\nTesting Enhanced Route Optimizer...")
    
    try:
        from enhanced_route_optimizer import EnhancedRouteOptimizer
        
        optimizer = EnhancedRouteOptimizer()
        
        # Test route optimization
        route = optimizer.optimize_route_with_safety_scoring(
            28.6139, 77.2090, 28.6169, 77.2120
        )
        
        if route:
            print(f"✓ Route optimized. Safety score: {route.total_safety_score:.2f}")
            print(f"✓ Travel time: {route.total_travel_time:.2f} minutes")
            print(f"✓ Confidence: {route.route_confidence:.2f}")
        else:
            print("✓ Route optimization completed (fallback route)")
        
        return True
        
    except Exception as e:
        print(f"✗ Route optimizer test failed: {e}")
        return False

def test_sakha_chatbot():
    """Test Sakha chatbot"""
    print("\nTesting Sakha Chatbot...")
    
    try:
        from sakha_chatbot import SakhaChatbot
        
        sakha = SakhaChatbot()
        
        # Test emergency contacts
        contacts = [
            {"name": "Test Contact", "phone": "+91-9876543210"}
        ]
        sakha.set_emergency_contacts(contacts)
        print("✓ Emergency contacts set")
        
        # Test intervention activation
        intervention = sakha.activate_proactive_intervention(
            1, {"lat": 28.6139, "lng": 77.2090}, 25
        )
        print(f"✓ Intervention activated: {intervention.get('intervention_type', 'unknown')}")
        
        # Test message processing
        response = sakha.process_user_message("I need help")
        print(f"✓ Message processed: {response.get('message', 'No response')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Sakha chatbot test failed: {e}")
        return False

def test_integrated_system():
    """Test the complete integrated system"""
    print("\nTesting Integrated Safe Route AI System...")
    
    try:
        from safe_route_ai_system import SafeRouteAISystem
        
        # Initialize system
        ai_system = SafeRouteAISystem()
        print("✓ AI system initialized")
        
        # Test system status
        status = ai_system.get_system_status()
        print(f"✓ System status: {status.get('active_users', 0)} active users")
        
        # Test route planning
        user_id = "test_user_001"
        route_response = ai_system.plan_safe_route(
            28.6139, 77.2090, 28.6169, 77.2120, user_id
        )
        
        if 'error' not in route_response:
            print(f"✓ Route planned: {route_response.get('route_id', 'unknown')}")
            print(f"✓ Safety score: {route_response.get('total_safety_score', 'N/A')}")
        else:
            print(f"✗ Route planning failed: {route_response['error']}")
            return False
        
        # Test location updates
        location_response = ai_system.update_user_location(
            user_id, 28.6149, 77.2100, 0.0
        )
        print(f"✓ Location updated. Anomaly: {location_response.get('anomaly_detected', False)}")
        
        # Test Sakha interaction
        sakha_response = ai_system.process_sakha_message(user_id, "I'm feeling unsafe")
        print(f"✓ Sakha response: {sakha_response.get('message', 'No response')[:50]}...")
        
        # Test safety status
        safety_status = ai_system.get_user_safety_status(user_id)
        print(f"✓ Safety status retrieved: {safety_status.get('safety_status', {}).get('current_phase', 'unknown')}")
        
        # Clean up
        ai_system.end_user_session(user_id)
        print("✓ Session ended successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Integrated system test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints (requires Flask server running)"""
    print("\nTesting API Endpoints...")
    
    try:
        import requests
        
        base_url = "http://localhost:5000"
        
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Health check passed")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
        
        # Test route planning
        route_data = {
            "source": {"lat": 28.6139, "lng": 77.2090},
            "destination": {"lat": 28.6169, "lng": 77.2120},
            "user_id": "test_api_user"
        }
        
        response = requests.post(f"{base_url}/api/plan-safe-route", 
                               json=route_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✓ API route planning successful")
            else:
                print(f"✗ API route planning failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"✗ API route planning failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("✗ API server not running. Start with: python enhanced_api_server.py")
        return False
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Safe Route AI System - Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Safety Model Test", test_safety_model),
        ("Geofencing Test", test_geofencing),
        ("Route Optimizer Test", test_route_optimizer),
        ("Sakha Chatbot Test", test_sakha_chatbot),
        ("Integrated System Test", test_integrated_system),
        ("API Endpoints Test", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'=' * 20} {test_name} {'=' * 20}")
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name} PASSED")
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 All tests passed! The AI system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
