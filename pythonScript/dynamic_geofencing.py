import numpy as np
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import time
import threading
from dataclasses import dataclass
from enum import Enum

class AlertPhase(Enum):
    NORMAL = "normal"
    SOFT_CHECK = "soft_check"
    ESCALATION = "escalation"
    EMERGENCY = "emergency"

@dataclass
class LocationData:
    lat: float
    lng: float
    timestamp: datetime
    speed: float = 0.0
    accuracy: float = 10.0

@dataclass
class SafetyZone:
    center_lat: float
    center_lng: float
    radius: float  # in meters
    safety_score: float
    zone_type: str  # 'safe', 'moderate', 'high_risk'

class DynamicGeofencing:
    def __init__(self, safety_model=None):
        self.safety_model = safety_model
        self.user_location_history = []
        self.planned_route = []
        self.safety_zones = []
        self.current_phase = AlertPhase.NORMAL
        self.anomaly_threshold = 5.0  # minutes
        self.speed_threshold = 1.0  # km/h (stopped)
        self.safety_score_threshold = 30  # Below this is considered unsafe
        
    def set_planned_route(self, route_coordinates: List[Tuple[float, float]]):
        """Set the planned safe route"""
        self.planned_route = route_coordinates
        self.safety_zones = self._create_safety_zones(route_coordinates)
    
    def _create_safety_zones(self, route_coordinates: List[Tuple[float, float]]):
        """Create safety zones along the planned route"""
        zones = []
        
        for i, (lat, lng) in enumerate(route_coordinates):
            if self.safety_model:
                safety_score = self.safety_model.predict_safety_score(lat, lng)
            else:
                safety_score = 50  # Default score
            
            zone_type = self._classify_zone_type(safety_score)
            radius = self._calculate_zone_radius(safety_score)
            
            zone = SafetyZone(
                center_lat=lat,
                center_lng=lng,
                radius=radius,
                safety_score=safety_score,
                zone_type=zone_type
            )
            zones.append(zone)
        
        return zones
    
    def _classify_zone_type(self, safety_score: float) -> str:
        """Classify zone type based on safety score"""
        if safety_score >= 70:
            return 'safe'
        elif safety_score >= 40:
            return 'moderate'
        else:
            return 'high_risk'
    
    def _calculate_zone_radius(self, safety_score: float) -> float:
        """Calculate zone radius based on safety score"""
        # Higher safety score = larger safe zone
        base_radius = 50  # meters
        safety_multiplier = safety_score / 100
        return base_radius + (safety_multiplier * 100)
    
    def update_user_location(self, lat: float, lng: float, speed: float = 0.0, accuracy: float = 10.0):
        """Update user location and check for anomalies"""
        current_location = LocationData(
            lat=lat,
            lng=lng,
            timestamp=datetime.now(),
            speed=speed,
            accuracy=accuracy
        )
        
        self.user_location_history.append(current_location)
        
        # Keep only last 100 locations
        if len(self.user_location_history) > 100:
            self.user_location_history = self.user_location_history[-100:]
        
        # Check for anomalies
        anomaly_detected = self._detect_anomalies(current_location)
        
        if anomaly_detected:
            self._handle_anomaly(current_location)
        
        return anomaly_detected
    
    def _detect_anomalies(self, current_location: LocationData) -> bool:
        """Detect behavioral anomalies"""
        if len(self.user_location_history) < 2:
            return False
        
        # Check if user has stopped in a low-safety area
        if self._is_stopped_in_unsafe_area(current_location):
            return True
        
        # Check if user has deviated significantly from planned route
        if self._has_deviated_from_route(current_location):
            return True
        
        # Check for unusual movement patterns
        if self._has_unusual_movement_pattern(current_location):
            return True
        
        return False
    
    def _is_stopped_in_unsafe_area(self, current_location: LocationData) -> bool:
        """Check if user is stopped in an unsafe area"""
        if current_location.speed > self.speed_threshold:
            return False
        
        # Get safety score for current location
        if self.safety_model:
            safety_score = self.safety_model.predict_safety_score(
                current_location.lat, 
                current_location.lng
            )
        else:
            safety_score = 50
        
        # Check if stopped for too long in unsafe area
        if safety_score < self.safety_score_threshold:
            stopped_duration = self._get_stopped_duration()
            if stopped_duration > self.anomaly_threshold:
                return True
        
        return False
    
    def _has_deviated_from_route(self, current_location: LocationData) -> bool:
        """Check if user has deviated significantly from planned route"""
        if not self.planned_route:
            return False
        
        # Find closest point on planned route
        min_distance = float('inf')
        for route_lat, route_lng in self.planned_route:
            distance = self._calculate_distance(
                current_location.lat, current_location.lng,
                route_lat, route_lng
            )
            min_distance = min(min_distance, distance)
        
        # If more than 200m from planned route, consider it a deviation
        return min_distance > 200
    
    def _has_unusual_movement_pattern(self, current_location: LocationData) -> bool:
        """Check for unusual movement patterns"""
        if len(self.user_location_history) < 5:
            return False
        
        # Check for erratic movement (rapid direction changes)
        recent_locations = self.user_location_history[-5:]
        direction_changes = 0
        
        for i in range(1, len(recent_locations) - 1):
            prev_bearing = self._calculate_bearing(
                recent_locations[i-1].lat, recent_locations[i-1].lng,
                recent_locations[i].lat, recent_locations[i].lng
            )
            curr_bearing = self._calculate_bearing(
                recent_locations[i].lat, recent_locations[i].lng,
                recent_locations[i+1].lat, recent_locations[i+1].lng
            )
            
            bearing_diff = abs(curr_bearing - prev_bearing)
            if bearing_diff > 180:
                bearing_diff = 360 - bearing_diff
            
            if bearing_diff > 90:  # Significant direction change
                direction_changes += 1
        
        # If more than 2 significant direction changes in 5 movements
        return direction_changes > 2
    
    def _get_stopped_duration(self) -> float:
        """Get duration user has been stopped (in minutes)"""
        if len(self.user_location_history) < 2:
            return 0
        
        stopped_start = None
        for location in reversed(self.user_location_history):
            if location.speed <= self.speed_threshold:
                if stopped_start is None:
                    stopped_start = location.timestamp
            else:
                break
        
        if stopped_start:
            return (datetime.now() - stopped_start).total_seconds() / 60
        
        return 0
    
    def _handle_anomaly(self, current_location: LocationData):
        """Handle detected anomaly"""
        if self.current_phase == AlertPhase.NORMAL:
            self.current_phase = AlertPhase.SOFT_CHECK
            self._trigger_soft_check_alert(current_location)
        elif self.current_phase == AlertPhase.SOFT_CHECK:
            # Check if user responded to soft check
            if not self._user_responded_to_soft_check():
                self.current_phase = AlertPhase.ESCALATION
                self._trigger_escalation_alert(current_location)
        elif self.current_phase == AlertPhase.ESCALATION:
            # Check if user responded to escalation
            if not self._user_responded_to_escalation():
                self.current_phase = AlertPhase.EMERGENCY
                self._trigger_emergency_alert(current_location)
    
    def _trigger_soft_check_alert(self, current_location: LocationData):
        """Trigger soft check alert"""
        alert_data = {
            "phase": "soft_check",
            "message": "It looks like you've paused in a low-safety area. Are you okay?",
            "location": {
                "lat": current_location.lat,
                "lng": current_location.lng
            },
            "timestamp": datetime.now().isoformat(),
            "actions": [
                "Tap to confirm you're okay",
                "Hold for 3 seconds to alert emergency contacts"
            ]
        }
        
        print(f"SOFT CHECK ALERT: {alert_data}")
        return alert_data
    
    def _trigger_escalation_alert(self, current_location: LocationData):
        """Trigger escalation alert"""
        alert_data = {
            "phase": "escalation",
            "message": "We're concerned about your safety. Sakha is here to help.",
            "location": {
                "lat": current_location.lat,
                "lng": current_location.lng
            },
            "timestamp": datetime.now().isoformat(),
            "sakha_ready": True,
            "emergency_contacts_prepared": True
        }
        
        print(f"ESCALATION ALERT: {alert_data}")
        return alert_data
    
    def _trigger_emergency_alert(self, current_location: LocationData):
        """Trigger emergency alert"""
        alert_data = {
            "phase": "emergency",
            "message": "EMERGENCY ALERT ACTIVATED",
            "location": {
                "lat": current_location.lat,
                "lng": current_location.lng
            },
            "timestamp": datetime.now().isoformat(),
            "emergency_contacts_notified": True,
            "police_alerted": True,
            "safety_score": self.safety_model.predict_safety_score(
                current_location.lat, current_location.lng
            ) if self.safety_model else 0
        }
        
        print(f"EMERGENCY ALERT: {alert_data}")
        return alert_data
    
    def _user_responded_to_soft_check(self) -> bool:
        """Check if user responded to soft check (simplified)"""
        # In real implementation, this would check user interaction
        return False  # Simulate no response for testing
    
    def _user_responded_to_escalation(self) -> bool:
        """Check if user responded to escalation (simplified)"""
        # In real implementation, this would check user interaction
        return False  # Simulate no response for testing
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points in meters"""
        R = 6371000  # Earth's radius in meters
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        a = (np.sin(dlat/2) * np.sin(dlat/2) + 
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * 
             np.sin(dlng/2) * np.sin(dlng/2))
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        return R * c
    
    def _calculate_bearing(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate bearing between two points"""
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        
        y = np.sin(dlng) * np.cos(np.radians(lat2))
        x = (np.cos(np.radians(lat1)) * np.sin(np.radians(lat2)) - 
             np.sin(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.cos(dlng))
        
        bearing = np.degrees(np.arctan2(y, x))
        return (bearing + 360) % 360
    
    def get_current_safety_status(self) -> Dict:
        """Get current safety status"""
        if not self.user_location_history:
            return {"status": "no_location_data"}
        
        current_location = self.user_location_history[-1]
        
        if self.safety_model:
            safety_score = self.safety_model.predict_safety_score(
                current_location.lat, current_location.lng
            )
        else:
            safety_score = 50
        
        return {
            "current_phase": self.current_phase.value,
            "safety_score": safety_score,
            "location": {
                "lat": current_location.lat,
                "lng": current_location.lng
            },
            "timestamp": current_location.timestamp.isoformat(),
            "speed": current_location.speed,
            "stopped_duration": self._get_stopped_duration()
        }

# Example usage
if __name__ == "__main__":
    # Initialize geofencing system
    geofencing = DynamicGeofencing()
    
    # Set a planned route (example coordinates)
    planned_route = [
        (28.6139, 77.2090),  # Start
        (28.6149, 77.2100),  # Waypoint 1
        (28.6159, 77.2110),  # Waypoint 2
        (28.6169, 77.2120)   # End
    ]
    
    geofencing.set_planned_route(planned_route)
    
    # Simulate user movement
    test_locations = [
        (28.6139, 77.2090, 0.0),  # Stopped at start
        (28.6149, 77.2100, 0.0),  # Stopped at waypoint
        (28.6159, 77.2110, 0.0),  # Stopped at another waypoint
    ]
    
    for lat, lng, speed in test_locations:
        anomaly = geofencing.update_user_location(lat, lng, speed)
        status = geofencing.get_current_safety_status()
        print(f"Location: ({lat}, {lng}), Anomaly: {anomaly}, Status: {status}")
