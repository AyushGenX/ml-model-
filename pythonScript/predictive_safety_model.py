import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
import requests
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os

class PredictiveSafetyModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour_of_day', 'day_of_week', 'month', 'is_weekend',
            'crime_density', 'lighting_score', 'traffic_density', 
            'business_density', 'population_density', 'historical_crime_score'
        ]
        
    def load_historical_data(self, crime_data_path='../data/crime.csv'):
        """Load and preprocess historical crime data"""
        try:
            df = pd.read_csv(crime_data_path)
            return df
        except Exception as e:
            print(f"Error loading crime data: {e}")
            return None
    
    def get_time_features(self, timestamp=None):
        """Extract time-based features"""
        if timestamp is None:
            timestamp = datetime.now()
        
        return {
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.weekday(),
            'month': timestamp.month,
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0
        }
    
    def get_lighting_score(self, lat, lng, hour):
        """Calculate lighting score based on time and location"""
        # Simulate lighting data - in real implementation, use Google Places API
        base_lighting = 50
        
        # Night time penalty
        if 18 <= hour or hour <= 6:
            lighting_penalty = 30
        elif 6 < hour < 18:
            lighting_penalty = 0
        else:
            lighting_penalty = 15
            
        # Business density affects lighting
        business_density = self.get_business_density(lat, lng)
        lighting_bonus = min(business_density * 2, 20)
        
        return max(0, min(100, base_lighting - lighting_penalty + lighting_bonus))
    
    def get_traffic_density(self, lat, lng, hour):
        """Get traffic density score"""
        # Simulate traffic data - in real implementation, use Google Maps Traffic API
        base_traffic = 50
        
        # Rush hour adjustments
        if 7 <= hour <= 9 or 17 <= hour <= 19:
            traffic_multiplier = 1.5
        elif 22 <= hour or hour <= 5:
            traffic_multiplier = 0.3
        else:
            traffic_multiplier = 1.0
            
        return min(100, base_traffic * traffic_multiplier)
    
    def get_business_density(self, lat, lng):
        """Get business density score"""
        # Simulate business density - in real implementation, use Google Places API
        # Higher business density = more lighting, people, safety
        return np.random.uniform(20, 80)
    
    def get_population_density(self, lat, lng):
        """Get population density score"""
        # Simulate population density
        return np.random.uniform(30, 90)
    
    def get_historical_crime_score(self, lat, lng, crime_data):
        """Calculate historical crime score for location"""
        # Find closest crime data point
        min_distance = float('inf')
        closest_crime_score = 5  # Default high risk
        
        for _, row in crime_data.iterrows():
            distance = np.sqrt((lat - row['lat'])**2 + (lng - row['long'])**2)
            if distance < min_distance:
                min_distance = distance
                closest_crime_score = row.get('crime/area', 5)
        
        # Convert to 0-100 scale (lower is safer)
        return max(0, min(100, 100 - (closest_crime_score * 10)))
    
    def create_feature_vector(self, lat, lng, timestamp=None, crime_data=None):
        """Create feature vector for prediction"""
        if timestamp is None:
            timestamp = datetime.now()
            
        features = self.get_time_features(timestamp)
        features['lighting_score'] = self.get_lighting_score(lat, lng, timestamp.hour)
        features['traffic_density'] = self.get_traffic_density(lat, lng, timestamp.hour)
        features['business_density'] = self.get_business_density(lat, lng)
        features['population_density'] = self.get_population_density(lat, lng)
        
        if crime_data is not None:
            features['historical_crime_score'] = self.get_historical_crime_score(lat, lng, crime_data)
        else:
            features['historical_crime_score'] = 50  # Default
            
        # Calculate crime density (simplified)
        features['crime_density'] = 100 - features['historical_crime_score']
        
        return features
    
    def train_model(self, training_data=None):
        """Train the predictive safety model"""
        if training_data is None:
            # Generate synthetic training data
            training_data = self.generate_synthetic_training_data()
        
        # Prepare features and target
        X = training_data[self.feature_columns]
        y = training_data['safety_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        print(f"Training Score: {train_score:.3f}")
        print(f"Test Score: {test_score:.3f}")
        
        # Save model
        self.save_model()
        
        return self.model
    
    def generate_synthetic_training_data(self, n_samples=1000):
        """Generate synthetic training data for model training"""
        data = []
        
        for _ in range(n_samples):
            # Random location in Delhi area
            lat = np.random.uniform(28.4, 28.8)
            lng = np.random.uniform(77.0, 77.4)
            
            # Random timestamp
            timestamp = datetime.now() - timedelta(days=np.random.randint(0, 365))
            
            # Create features
            features = self.create_feature_vector(lat, lng, timestamp)
            
            # Generate synthetic safety score based on features
            safety_score = self.calculate_synthetic_safety_score(features)
            
            features['safety_score'] = safety_score
            data.append(features)
        
        return pd.DataFrame(data)
    
    def calculate_synthetic_safety_score(self, features):
        """Calculate synthetic safety score based on features"""
        score = 50  # Base score
        
        # Time-based adjustments
        if features['hour_of_day'] >= 22 or features['hour_of_day'] <= 5:
            score -= 20  # Night time penalty
        elif 6 <= features['hour_of_day'] <= 18:
            score += 10  # Day time bonus
            
        # Weekend penalty
        if features['is_weekend']:
            score -= 5
            
        # Lighting bonus
        score += (features['lighting_score'] - 50) * 0.3
        
        # Traffic bonus (more traffic = safer)
        score += (features['traffic_density'] - 50) * 0.2
        
        # Business density bonus
        score += (features['business_density'] - 50) * 0.2
        
        # Crime penalty
        score -= (features['crime_density'] - 50) * 0.4
        
        return max(0, min(100, score))
    
    def predict_safety_score(self, lat, lng, timestamp=None, crime_data=None):
        """Predict safety score for given location and time"""
        if self.model is None:
            self.load_model()
        
        if self.model is None:
            print("Model not trained. Training now...")
            self.train_model()
        
        # Create feature vector
        features = self.create_feature_vector(lat, lng, timestamp, crime_data)
        
        # Convert to DataFrame
        feature_df = pd.DataFrame([features])
        
        # Scale features
        feature_scaled = self.scaler.transform(feature_df[self.feature_columns])
        
        # Predict
        safety_score = self.model.predict(feature_scaled)[0]
        
        return max(0, min(100, safety_score))
    
    def save_model(self, model_path='models/safety_model.pkl'):
        """Save trained model"""
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }, model_path)
        print(f"Model saved to {model_path}")
    
    def load_model(self, model_path='models/safety_model.pkl'):
        """Load trained model"""
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_columns = model_data['feature_columns']
                print(f"Model loaded from {model_path}")
                return True
        except Exception as e:
            print(f"Error loading model: {e}")
        return False

# Example usage
if __name__ == "__main__":
    # Initialize model
    safety_model = PredictiveSafetyModel()
    
    # Load crime data
    crime_data = safety_model.load_historical_data()
    
    # Train model
    safety_model.train_model()
    
    # Test prediction
    test_lat, test_lng = 28.6139, 77.2090  # Delhi coordinates
    safety_score = safety_model.predict_safety_score(test_lat, test_lng, crime_data=crime_data)
    print(f"Predicted safety score for Delhi: {safety_score:.2f}")
