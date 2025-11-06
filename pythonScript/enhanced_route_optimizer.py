import numpy as np
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import requests
from dataclasses import dataclass

@dataclass
class RoutePoint:
    lat: float
    lng: float
    safety_score: float
    timestamp: datetime
    estimated_travel_time: float  # minutes

@dataclass
class OptimizedRoute:
    points: List[RoutePoint]
    total_safety_score: float
    total_travel_time: float
    route_confidence: float

class EnhancedRouteOptimizer:
    def __init__(self, safety_model=None, google_maps_api_key=None):
        self.safety_model = safety_model
        self.google_maps_api_key = google_maps_api_key
        self.route_cache = {}
        
    def optimize_route_with_safety_scoring(self, 
                                         start_lat: float, 
                                         start_lng: float,
                                         end_lat: float, 
                                         end_lng: float,
                                         departure_time: Optional[datetime] = None,
                                         max_alternatives: int = 3) -> OptimizedRoute:
        """
        Optimize route using predictive safety scoring
        """
        if departure_time is None:
            departure_time = datetime.now()
        
        # Get multiple route alternatives from Google Maps
        route_alternatives = self._get_route_alternatives(
            start_lat, start_lng, end_lat, end_lng, max_alternatives
        )
        
        if not route_alternatives:
            return self._create_fallback_route(start_lat, start_lng, end_lat, end_lng)
        
        # Calculate safety scores for each route
        optimized_routes = []
        
        for route in route_alternatives:
            safety_optimized_route = self._calculate_route_safety_scores(
                route, departure_time
            )
            optimized_routes.append(safety_optimized_route)
        
        # Select the best route based on cumulative safety score
        best_route = self._select_best_route(optimized_routes)
        
        return best_route
    
    def _get_route_alternatives(self, start_lat: float, start_lng: float, 
                               end_lat: float, end_lng: float, 
                               max_alternatives: int) -> List[Dict]:
        """Get route alternatives from Google Maps API"""
        if not self.google_maps_api_key:
            return self._get_mock_routes(start_lat, start_lng, end_lat, end_lng)
        
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': f"{start_lat},{start_lng}",
                'destination': f"{end_lat},{end_lng}",
                'alternatives': 'true',
                'mode': 'driving',
                'avoid': 'highways',
                'key': self.google_maps_api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'OK':
                return data['routes'][:max_alternatives]
            else:
                print(f"Google Maps API error: {data['status']}")
                return self._get_mock_routes(start_lat, start_lng, end_lat, end_lng)
                
        except Exception as e:
            print(f"Error getting routes from Google Maps: {e}")
            return self._get_mock_routes(start_lat, start_lng, end_lat, end_lng)
    
    def _get_mock_routes(self, start_lat: float, start_lng: float, 
                        end_lat: float, end_lng: float) -> List[Dict]:
        """Generate mock routes for testing"""
        # Create a simple straight-line route with some waypoints
        num_waypoints = 5
        lat_step = (end_lat - start_lat) / num_waypoints
        lng_step = (end_lng - start_lng) / num_waypoints
        
        steps = []
        for i in range(num_waypoints + 1):
            lat = start_lat + (lat_step * i)
            lng = start_lng + (lng_step * i)
            
            step = {
                'start_location': {'lat': lat, 'lng': lng},
                'end_location': {'lat': lat + lat_step/2, 'lng': lng + lng_step/2},
                'duration': {'value': 300}  # 5 minutes per step
            }
            steps.append(step)
        
        return [{
            'legs': [{'steps': steps}],
            'summary': 'Mock Route'
        }]
    
    def _calculate_route_safety_scores(self, route: Dict, departure_time: datetime) -> OptimizedRoute:
        """Calculate safety scores for each point in the route"""
        points = []
        current_time = departure_time
        total_safety_score = 0
        total_travel_time = 0
        
        for step in route['legs'][0]['steps']:
            start_lat = step['start_location']['lat']
            start_lng = step['start_location']['lng']
            
            # Calculate safety score for this point
            if self.safety_model:
                safety_score = self.safety_model.predict_safety_score(
                    start_lat, start_lng, current_time
                )
            else:
                safety_score = 50  # Default score
            
            # Calculate travel time for this step
            step_duration = step['duration']['value'] / 60  # Convert to minutes
            
            # Create route point
            route_point = RoutePoint(
                lat=start_lat,
                lng=start_lng,
                safety_score=safety_score,
                timestamp=current_time,
                estimated_travel_time=step_duration
            )
            
            points.append(route_point)
            total_safety_score += safety_score
            total_travel_time += step_duration
            
            # Update time for next step
            current_time += timedelta(minutes=step_duration)
        
        # Calculate route confidence based on safety score consistency
        safety_scores = [point.safety_score for point in points]
        route_confidence = self._calculate_route_confidence(safety_scores)
        
        return OptimizedRoute(
            points=points,
            total_safety_score=total_safety_score,
            total_travel_time=total_travel_time,
            route_confidence=route_confidence
        )
    
    def _calculate_route_confidence(self, safety_scores: List[float]) -> float:
        """Calculate confidence in route safety based on score consistency"""
        if not safety_scores:
            return 0.0
        
        # Higher confidence for consistent high scores
        mean_score = np.mean(safety_scores)
        std_score = np.std(safety_scores)
        
        # Confidence decreases with high variance
        consistency_factor = max(0, 1 - (std_score / 50))
        
        # Confidence increases with higher mean scores
        score_factor = mean_score / 100
        
        return min(1.0, (consistency_factor + score_factor) / 2)
    
    def _select_best_route(self, routes: List[OptimizedRoute]) -> OptimizedRoute:
        """Select the best route based on safety score and travel time"""
        if not routes:
            return None
        
        # Calculate composite score for each route
        route_scores = []
        
        for route in routes:
            # Normalize safety score (0-1)
            normalized_safety = route.total_safety_score / (len(route.points) * 100)
            
            # Normalize travel time (inverse relationship - shorter is better)
            # Assuming max reasonable travel time is 60 minutes
            normalized_time = max(0, 1 - (route.total_travel_time / 60))
            
            # Weighted composite score
            composite_score = (normalized_safety * 0.7) + (normalized_time * 0.3)
            
            route_scores.append(composite_score)
        
        # Select route with highest composite score
        best_route_index = np.argmax(route_scores)
        return routes[best_route_index]
    
    def _create_fallback_route(self, start_lat: float, start_lng: float, 
                              end_lat: float, end_lng: float) -> OptimizedRoute:
        """Create a simple fallback route"""
        points = [
            RoutePoint(
                lat=start_lat,
                lng=start_lng,
                safety_score=50,
                timestamp=datetime.now(),
                estimated_travel_time=0
            ),
            RoutePoint(
                lat=end_lat,
                lng=end_lng,
                safety_score=50,
                timestamp=datetime.now() + timedelta(minutes=30),
                estimated_travel_time=30
            )
        ]
        
        return OptimizedRoute(
            points=points,
            total_safety_score=100,
            total_travel_time=30,
            route_confidence=0.5
        )
    
    def get_real_time_safety_updates(self, route: OptimizedRoute, 
                                   current_location: Tuple[float, float]) -> Dict:
        """Get real-time safety updates for current location"""
        current_lat, current_lng = current_location
        
        # Find closest point on route
        closest_point = None
        min_distance = float('inf')
        
        for point in route.points:
            distance = self._calculate_distance(
                current_lat, current_lng, point.lat, point.lng
            )
            if distance < min_distance:
                min_distance = distance
                closest_point = point
        
        # Get current safety score
        if self.safety_model:
            current_safety_score = self.safety_model.predict_safety_score(
                current_lat, current_lng
            )
        else:
            current_safety_score = 50
        
        # Calculate safety trend
        safety_trend = self._calculate_safety_trend(route, current_location)
        
        return {
            "current_safety_score": current_safety_score,
            "planned_safety_score": closest_point.safety_score if closest_point else 50,
            "safety_trend": safety_trend,
            "distance_from_route": min_distance,
            "recommendations": self._generate_safety_recommendations(
                current_safety_score, safety_trend
            )
        }
    
    def _calculate_safety_trend(self, route: OptimizedRoute, 
                              current_location: Tuple[float, float]) -> str:
        """Calculate safety trend for upcoming route"""
        current_lat, current_lng = current_location
        
        # Find current position in route
        current_index = 0
        min_distance = float('inf')
        
        for i, point in enumerate(route.points):
            distance = self._calculate_distance(
                current_lat, current_lng, point.lat, point.lng
            )
            if distance < min_distance:
                min_distance = distance
                current_index = i
        
        # Calculate average safety score for remaining route
        remaining_points = route.points[current_index:]
        if len(remaining_points) < 2:
            return "stable"
        
        remaining_scores = [point.safety_score for point in remaining_points]
        avg_remaining = np.mean(remaining_scores)
        current_score = remaining_scores[0] if remaining_scores else 50
        
        if avg_remaining > current_score + 10:
            return "improving"
        elif avg_remaining < current_score - 10:
            return "deteriorating"
        else:
            return "stable"
    
    def _generate_safety_recommendations(self, current_score: float, trend: str) -> List[str]:
        """Generate safety recommendations based on current score and trend"""
        recommendations = []
        
        if current_score < 30:
            recommendations.append("High risk area - consider alternative route")
            recommendations.append("Stay alert and avoid isolated areas")
        elif current_score < 50:
            recommendations.append("Moderate risk - stay aware of surroundings")
        
        if trend == "deteriorating":
            recommendations.append("Safety conditions worsening ahead")
        elif trend == "improving":
            recommendations.append("Safety conditions improving ahead")
        
        if current_score >= 70:
            recommendations.append("Safe area - good lighting and activity")
        
        return recommendations
    
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

# Example usage
if __name__ == "__main__":
    # Initialize route optimizer
    optimizer = EnhancedRouteOptimizer()
    
    # Test route optimization
    start_lat, start_lng = 28.6139, 77.2090  # Delhi
    end_lat, end_lng = 28.6169, 77.2120
    
    optimized_route = optimizer.optimize_route_with_safety_scoring(
        start_lat, start_lng, end_lat, end_lng
    )
    
    print(f"Optimized Route:")
    print(f"Total Safety Score: {optimized_route.total_safety_score:.2f}")
    print(f"Total Travel Time: {optimized_route.total_travel_time:.2f} minutes")
    print(f"Route Confidence: {optimized_route.route_confidence:.2f}")
    
    # Test real-time updates
    current_location = (28.6149, 77.2100)
    updates = optimizer.get_real_time_safety_updates(optimized_route, current_location)
    print(f"\nReal-time Updates: {updates}")
