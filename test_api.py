#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import json

def test_ai_api():
    """Test the AI API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🧪 Testing AI API endpoints...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Status: {response.json().get('status')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test route planning
    print("\n2. Testing route planning...")
    try:
        route_data = {
            "source": {"lat": 28.6139, "lng": 77.2090},
            "destination": {"lat": 28.6169, "lng": 77.2120},
            "user_id": "test_user_001"
        }
        
        response = requests.post(f"{base_url}/api/plan-safe-route", json=route_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                route_info = data['data']
                print("✅ Route planning successful")
                print(f"   Route ID: {route_info.get('route_id')}")
                print(f"   Safety Score: {route_info.get('total_safety_score', 'N/A')}")
                print(f"   Travel Time: {route_info.get('total_travel_time', 'N/A')} minutes")
            else:
                print(f"❌ Route planning failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Route planning failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Route planning error: {e}")
        return False
    
    # Test location update
    print("\n3. Testing location update...")
    try:
        location_data = {
            "user_id": "test_user_001",
            "location": {"lat": 28.6149, "lng": 77.2100},
            "speed": 0.0
        }
        
        response = requests.post(f"{base_url}/api/update-location", json=location_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Location update successful")
                print(f"   Anomaly detected: {data['data'].get('anomaly_detected', False)}")
            else:
                print(f"❌ Location update failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Location update failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Location update error: {e}")
        return False
    
    # Test Sakha chat
    print("\n4. Testing Sakha chat...")
    try:
        chat_data = {
            "user_id": "test_user_001",
            "message": "I'm feeling unsafe"
        }
        
        response = requests.post(f"{base_url}/api/sakha-chat", json=chat_data)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Sakha chat successful")
                print(f"   Response: {data['data'].get('message', 'No response')[:50]}...")
            else:
                print(f"❌ Sakha chat failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Sakha chat failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sakha chat error: {e}")
        return False
    
    print("\n🎉 All API tests passed! The AI system is working perfectly.")
    return True

if __name__ == "__main__":
    test_ai_api()
