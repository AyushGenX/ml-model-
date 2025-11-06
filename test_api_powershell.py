#!/usr/bin/env python3
"""
PowerShell-compatible API test script
"""

import requests
import json

def test_route_planning():
    """Test route planning endpoint"""
    print("🧪 Testing AI Route Planning...")
    
    try:
        url = "http://localhost:5000/api/plan-safe-route"
        data = {
            "source": {"lat": 28.6139, "lng": 77.2090},
            "destination": {"lat": 28.6169, "lng": 77.2120},
            "user_id": "test_user_powershell"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                route_info = result['data']
                print("✅ Route planning successful!")
                print(f"   Route ID: {route_info.get('route_id')}")
                print(f"   Safety Score: {route_info.get('total_safety_score', 'N/A')}")
                print(f"   Travel Time: {route_info.get('total_travel_time', 'N/A')} minutes")
                print(f"   Route Confidence: {route_info.get('route_confidence', 'N/A')}")
                return route_info.get('route_id')
            else:
                print(f"❌ Route planning failed: {result.get('error')}")
                return None
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_location_update(user_id):
    """Test location update endpoint"""
    print("\n🧪 Testing Location Update...")
    
    try:
        url = "http://localhost:5000/api/update-location"
        data = {
            "user_id": user_id,
            "location": {"lat": 28.6149, "lng": 77.2100},
            "speed": 0.0
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Location update successful!")
                print(f"   Anomaly detected: {result['data'].get('anomaly_detected', False)}")
                if result['data'].get('sakha_intervention'):
                    print(f"   Sakha intervention: {result['data']['sakha_intervention'].get('intervention_type', 'unknown')}")
                return True
            else:
                print(f"❌ Location update failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sakha_chat(user_id):
    """Test Sakha chatbot endpoint"""
    print("\n🧪 Testing Sakha Chatbot...")
    
    try:
        url = "http://localhost:5000/api/sakha-chat"
        data = {
            "user_id": user_id,
            "message": "I'm feeling unsafe and need help"
        }
        
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Sakha chat successful!")
                print(f"   Response: {result['data'].get('message', 'No response')[:100]}...")
                return True
            else:
                print(f"❌ Sakha chat failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_safety_status(user_id):
    """Test safety status endpoint"""
    print("\n🧪 Testing Safety Status...")
    
    try:
        url = f"http://localhost:5000/api/safety-status/{user_id}"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Safety status retrieved!")
                safety_status = result['data'].get('safety_status', {})
                print(f"   Current phase: {safety_status.get('current_phase', 'unknown')}")
                print(f"   Safety score: {safety_status.get('safety_score', 'N/A')}")
                return True
            else:
                print(f"❌ Safety status failed: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Safe Route AI System - PowerShell Test Suite")
    print("=" * 60)
    
    # Test route planning
    route_id = test_route_planning()
    if not route_id:
        print("\n❌ Route planning failed. Cannot continue with other tests.")
        return False
    
    user_id = "test_user_powershell"
    
    # Test location update
    if not test_location_update(user_id):
        print("\n⚠️  Location update failed, but continuing...")
    
    # Test Sakha chat
    if not test_sakha_chat(user_id):
        print("\n⚠️  Sakha chat failed, but continuing...")
    
    # Test safety status
    if not test_safety_status(user_id):
        print("\n⚠️  Safety status failed, but continuing...")
    
    print("\n" + "=" * 60)
    print("🎉 PowerShell API tests completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    main()
