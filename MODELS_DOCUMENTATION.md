# Safe Route AI - Models & Algorithms Documentation

This document provides comprehensive documentation of all machine learning models, algorithms, and AI components used in the Safe Route AI system.

## Table of Contents

1. [Machine Learning Models](#machine-learning-models)
2. [Algorithms & Techniques](#algorithms--techniques)
3. [Data Processing Components](#data-processing-components)
4. [AI Components](#ai-components)
5. [Model Architecture](#model-architecture)
6. [Model Training & Evaluation](#model-training--evaluation)
7. [Model Storage & Loading](#model-storage--loading)
8. [Dependencies](#dependencies)

---

## Machine Learning Models

### 1. Predictive Safety Model (Random Forest Regressor)

**Purpose**: Predicts safety scores (0-100) for any geographic location based on multiple contextual factors.

**Model Type**: Supervised Learning - Regression  
**Algorithm**: Random Forest Regressor  
**Library**: scikit-learn (`sklearn.ensemble.RandomForestRegressor`)

#### Model Configuration
- **Number of Estimators**: 100 trees
- **Random State**: 42 (for reproducibility)
- **Feature Scaling**: StandardScaler (mean=0, std=1)
- **Train-Test Split**: 80-20 (test_size=0.2)

#### Features (11 features)
1. **Time-based Features**:
   - `hour_of_day` (0-23): Current hour
   - `day_of_week` (0-6): Day of week (Monday=0, Sunday=6)
   - `month` (1-12): Current month
   - `is_weekend` (0 or 1): Binary indicator

2. **Location-based Features**:
   - `crime_density` (0-100): Calculated from historical crime data
   - `lighting_score` (0-100): Lighting conditions based on time and business density
   - `traffic_density` (0-100): Traffic density based on time of day
   - `business_density` (0-100): Density of businesses/commercial activity
   - `population_density` (0-100): Population density in area
   - `historical_crime_score` (0-100): Historical crime data score

#### Model Location
- **File**: `pythonScript/predictive_safety_model.py`
- **Saved Model**: `models/safety_model.pkl`
- **Class**: `PredictiveSafetyModel`

#### Training Data
- **Data Source**: Synthetic training data (1000 samples)
- **Data Generation**: `generate_synthetic_training_data()` method
- **Real Data**: Historical crime data from `data/crime.csv`

#### Output
- **Safety Score**: Float value between 0-100
  - 0-30: High risk
  - 30-50: Moderate risk
  - 50-70: Safe
  - 70-100: Very safe

#### Model Performance
- Training and test scores are calculated using R² score
- Model is evaluated during training and scores are printed

---

### 2. K-Means Clustering Model

**Purpose**: Clusters crime data areas into groups based on crime characteristics for analysis and visualization.

**Model Type**: Unsupervised Learning - Clustering  
**Algorithm**: K-Means Clustering  
**Library**: scikit-learn (`sklearn.cluster.KMeans`)

#### Model Configuration
- **Number of Clusters**: 6 clusters
- **Initialization**: k-means++ (smart initialization)
- **Random State**: 42
- **Elbow Method**: Used to determine optimal number of clusters (tested 1-20)

#### Features Used
- Crime data features from `data/crime.csv`:
  - Columns: [1,2,3,4,5,6,7,12] (crime statistics, area metrics)

#### Feature Scaling
- **Scaler**: StandardScaler
- **Method**: Standardization (mean=0, std=1)

#### Dimensionality Reduction
- **Method**: Kernel PCA (Principal Component Analysis)
- **Kernel**: RBF (Radial Basis Function)
- **Components**: 2 (for visualization)

#### Model Location
- **File**: `pythonScript/kmeans.py`

#### Output
- **Cluster Labels**: Integer labels (0-5) for each data point
- **Cluster Centroids**: Center points of each cluster
- **Visualization**: 2D scatter plot with cluster assignments

---

## Algorithms & Techniques

### 3. Route Optimization Algorithm

**Purpose**: Selects the safest route among multiple alternatives by calculating composite scores.

**Algorithm Type**: Heuristic Optimization  
**Location**: `pythonScript/enhanced_route_optimizer.py`

#### Algorithm Steps
1. **Route Alternative Generation**: Get multiple route alternatives from Google Maps API
2. **Safety Scoring**: Calculate safety score for each point in each route using Predictive Safety Model
3. **Composite Scoring**: Calculate weighted composite score for each route
4. **Route Selection**: Select route with highest composite score

#### Composite Score Formula
```
composite_score = (normalized_safety * 0.7) + (normalized_time * 0.3)
```
Where:
- `normalized_safety` = total_safety_score / (number_of_points * 100)
- `normalized_time` = max(0, 1 - (travel_time / 60))

#### Route Confidence Calculation
```
consistency_factor = max(0, 1 - (std_score / 50))
score_factor = mean_score / 100
confidence = (consistency_factor + score_factor) / 2
```

---

### 4. Anomaly Detection Algorithms

**Purpose**: Detects unusual patterns in user movement and location data to trigger safety alerts.

**Algorithm Type**: Pattern Recognition / Rule-based  
**Location**: `pythonScript/dynamic_geofencing.py`

#### Detection Methods

##### 4.1 Stopped in Unsafe Area Detection
- **Threshold**: Speed < 1.0 km/h
- **Safety Threshold**: Safety score < 30
- **Duration Threshold**: Stopped for > 5 minutes
- **Algorithm**: Checks if user is stationary in low-safety area for extended period

##### 4.2 Route Deviation Detection
- **Threshold**: Distance > 200 meters from planned route
- **Algorithm**: Calculates minimum distance from user location to any point on planned route using Haversine distance

##### 4.3 Unusual Movement Pattern Detection
- **Method**: Direction change analysis
- **Threshold**: > 2 significant direction changes (>90°) in last 5 movements
- **Algorithm**: Calculates bearing changes between consecutive location points

#### Phased Alert System
1. **Soft Check**: Initial gentle notification
2. **Escalation**: Sakha chatbot activation
3. **Emergency**: Automatic emergency service contact

---

### 5. Distance Calculation Algorithms

#### 5.1 Haversine Distance Formula

**Purpose**: Calculate great-circle distance between two geographic points.

**Formula**:
```
a = sin²(Δlat/2) + cos(lat1) × cos(lat2) × sin²(Δlng/2)
c = 2 × atan2(√a, √(1-a))
distance = R × c
```
Where:
- R = Earth's radius (6,371,000 meters)
- lat1, lng1 = First point coordinates
- lat2, lng2 = Second point coordinates

**Usage**: 
- Route deviation detection
- Finding closest route point
- Distance calculations in geofencing

#### 5.2 Bearing Calculation

**Purpose**: Calculate direction (bearing) between two geographic points.

**Formula**:
```
y = sin(Δlng) × cos(lat2)
x = cos(lat1) × sin(lat2) - sin(lat1) × cos(lat2) × cos(Δlng)
bearing = atan2(y, x)
```

**Usage**: 
- Movement pattern analysis
- Direction change detection

**Location**: `pythonScript/dynamic_geofencing.py` (lines 310-320)

---

### 6. Safety Score Calculation Algorithms

#### 6.1 Lighting Score Algorithm
- **Base Score**: 50
- **Night Time Penalty**: -30 (6 PM - 6 AM)
- **Day Time Bonus**: 0 penalty (6 AM - 6 PM)
- **Business Density Bonus**: min(business_density * 2, 20)
- **Final Score**: max(0, min(100, base + bonuses - penalties))

#### 6.2 Traffic Density Algorithm
- **Base Traffic**: 50
- **Rush Hour Multiplier**: 1.5 (7-9 AM, 5-7 PM)
- **Night Time Multiplier**: 0.3 (10 PM - 5 AM)
- **Normal Time Multiplier**: 1.0
- **Final Score**: base_traffic × multiplier (capped at 100)

#### 6.3 Historical Crime Score Algorithm
- **Method**: Nearest neighbor search
- **Distance Metric**: Euclidean distance in lat/lng space
- **Score Conversion**: 100 - (crime_density × 10)
- **Default**: 50 (if no crime data available)

#### 6.4 Synthetic Safety Score (Training Data Generation)
```
score = 50  # Base
- Night time penalty: -20 (10 PM - 5 AM)
+ Day time bonus: +10 (6 AM - 6 PM)
- Weekend penalty: -5
+ Lighting bonus: (lighting_score - 50) × 0.3
+ Traffic bonus: (traffic_density - 50) × 0.2
+ Business bonus: (business_density - 50) × 0.2
- Crime penalty: (crime_density - 50) × 0.4
Final: max(0, min(100, score))
```

---

## Data Processing Components

### 7. StandardScaler

**Purpose**: Standardize features by removing mean and scaling to unit variance.

**Library**: scikit-learn (`sklearn.preprocessing.StandardScaler`)

**Formula**:
```
z = (x - μ) / σ
```
Where:
- μ = mean of feature
- σ = standard deviation of feature

**Usage**:
- Predictive Safety Model feature scaling
- K-Means clustering preprocessing

**Location**: Used in:
- `pythonScript/predictive_safety_model.py`
- `pythonScript/kmeans.py`

---

### 8. Kernel PCA (Principal Component Analysis)

**Purpose**: Reduce dimensionality of crime data for visualization.

**Library**: scikit-learn (`sklearn.decomposition.KernelPCA`)

**Configuration**:
- **Kernel**: RBF (Radial Basis Function)
- **Components**: 2 (for 2D visualization)

**Usage**: 
- Visualizing K-Means clusters
- Reducing 8-dimensional crime data to 2D for plotting

**Location**: `pythonScript/kmeans.py` (line 36-38)

---

## AI Components

### 9. Sakha Chatbot (Rule-based AI)

**Purpose**: Provides contextual safety assistance and emergency support through conversational interface.

**Type**: Rule-based AI (Keyword Matching)  
**Location**: `pythonScript/sakha_chatbot.py`

#### Intent Recognition Algorithm
- **Method**: Keyword-based pattern matching
- **Intents Detected**:
  - Emergency: "help", "emergency", "danger", "scared", "unsafe", "threat"
  - Safety Confirmation: "okay", "fine", "safe", "good", "alright"
  - Legal Advice: "rights", "legal", "police", "law", "report"
  - Emotional Support: "scared", "worried", "anxious", "fear", "nervous"
  - Greeting: "hello", "hi", "hey", "good morning"

#### Sentiment Analysis Algorithm
- **Method**: Word count-based sentiment analysis
- **Positive Words**: "good", "fine", "safe", "okay", "better", "calm"
- **Negative Words**: "bad", "scared", "worried", "unsafe", "danger", "fear"
- **Output**: "positive", "negative", or "neutral"

#### Response Generation
- **Method**: Template-based response selection
- **Templates**: Pre-defined response templates for each intent
- **Selection**: Random selection from template pool for variety

#### State Management
- **States**: IDLE, ACTIVE, EMERGENCY, SUPPORT
- **State Transitions**: Based on alert level and user interactions

---

## Model Architecture

### System Integration

```
Safe Route AI System
│
├── Predictive Safety Model (Random Forest)
│   ├── Feature Engineering
│   ├── Model Training
│   └── Safety Score Prediction
│
├── Enhanced Route Optimizer
│   ├── Route Alternative Generation
│   ├── Safety Score Calculation (uses Safety Model)
│   ├── Composite Scoring
│   └── Best Route Selection
│
├── Dynamic Geofencing
│   ├── Anomaly Detection
│   ├── Route Deviation Detection
│   ├── Movement Pattern Analysis
│   └── Alert Phase Management
│
└── Sakha Chatbot
    ├── Intent Recognition
    ├── Sentiment Analysis
    └── Response Generation
```

### Data Flow

1. **User Input** → Route planning request
2. **Route Optimizer** → Gets route alternatives from Google Maps
3. **Safety Model** → Calculates safety scores for each route point
4. **Route Optimizer** → Selects best route based on composite score
5. **Geofencing** → Monitors user location during navigation
6. **Anomaly Detection** → Detects unusual patterns
7. **Sakha Chatbot** → Provides assistance if anomalies detected

---

## Model Training & Evaluation

### Predictive Safety Model Training

#### Training Process
1. **Data Generation**: Generate 1000 synthetic training samples
2. **Feature Extraction**: Extract 11 features for each sample
3. **Data Splitting**: 80% training, 20% testing
4. **Feature Scaling**: Standardize features using StandardScaler
5. **Model Training**: Train Random Forest with 100 estimators
6. **Evaluation**: Calculate R² scores for train and test sets
7. **Model Saving**: Save model, scaler, and feature columns to `models/safety_model.pkl`

#### Training Code Location
- **File**: `pythonScript/predictive_safety_model.py`
- **Method**: `train_model()` (lines 124-155)

#### Evaluation Metrics
- **Training Score**: R² score on training data
- **Test Score**: R² score on test data
- **Output Range**: Safety scores clamped to [0, 100]

### K-Means Clustering Training

#### Training Process
1. **Data Loading**: Load crime data from CSV
2. **Feature Selection**: Select relevant columns [1,2,3,4,5,6,7,12]
3. **Feature Scaling**: Standardize features
4. **Elbow Method**: Determine optimal number of clusters (1-20)
5. **Model Training**: Fit K-Means with 6 clusters
6. **Dimensionality Reduction**: Apply Kernel PCA for visualization
7. **Visualization**: Plot clusters in 2D space

#### Training Code Location
- **File**: `pythonScript/kmeans.py`

---

## Model Storage & Loading

### Model Persistence

#### Predictive Safety Model
- **Storage Format**: Pickle (joblib)
- **File Path**: `models/safety_model.pkl`
- **Stored Components**:
  - Trained Random Forest model
  - StandardScaler object
  - Feature column names

#### Loading Process
1. Check if model file exists
2. Load model data using `joblib.load()`
3. Restore model, scaler, and feature columns
4. If loading fails, train new model

#### Code Location
- **Save**: `predictive_safety_model.py` - `save_model()` (lines 231-239)
- **Load**: `predictive_safety_model.py` - `load_model()` (lines 241-253)

---

## Dependencies

### Python Libraries

#### Core ML Libraries
- **scikit-learn** (>=1.0.0): Machine learning algorithms
  - `RandomForestRegressor`: Predictive safety model
  - `KMeans`: Clustering
  - `StandardScaler`: Feature scaling
  - `KernelPCA`: Dimensionality reduction
  - `train_test_split`: Data splitting

#### Data Processing
- **numpy** (>=1.21.0): Numerical computations
- **pandas** (>=1.3.0): Data manipulation
- **joblib** (>=1.1.0): Model serialization

#### Visualization
- **matplotlib** (>=3.5.0): Plotting and visualization

#### Web Framework
- **Flask** (>=2.0.0): API server
- **Flask-CORS** (>=3.0.0): Cross-origin resource sharing

#### HTTP Requests
- **requests** (>=2.25.0): API calls to Google Maps

### Optional Dependencies (Commented Out)
- **tensorflow** (>=2.8.0): Deep learning (not currently used)
- **torch** (>=1.10.0): PyTorch (not currently used)

### Installation
```bash
pip install -r requirements.txt
```

---

## Model Performance & Limitations

### Predictive Safety Model

#### Strengths
- Handles non-linear relationships well
- Provides feature importance (through Random Forest)
- Robust to outliers
- Fast prediction time (<100ms)

#### Limitations
- Trained on synthetic data (may not reflect real-world patterns accurately)
- Requires historical crime data for best performance
- Lighting and traffic data are simulated (not from real APIs)
- Model accuracy depends on quality of training data

### K-Means Clustering

#### Strengths
- Simple and interpretable
- Fast clustering algorithm
- Good for exploratory data analysis

#### Limitations
- Requires pre-specification of number of clusters
- Sensitive to initialization
- Assumes spherical clusters
- May not work well with non-spherical cluster shapes

### Anomaly Detection

#### Strengths
- Real-time detection
- Multiple detection methods
- Phased alert system prevents false alarms

#### Limitations
- Rule-based (may miss complex patterns)
- Thresholds may need tuning for different regions
- No learning from user behavior over time

---

## Future Improvements

### Potential Model Enhancements

1. **Deep Learning Models**
   - Replace Random Forest with Neural Networks for better accuracy
   - Use LSTM for time-series safety prediction
   - Implement CNN for geographic pattern recognition

2. **Real Data Integration**
   - Integrate real-time lighting data from Google Places API
   - Use actual traffic data from Google Maps Traffic API
   - Incorporate real-time crime reports

3. **Advanced Anomaly Detection**
   - Implement isolation forests for anomaly detection
   - Use autoencoders for pattern recognition
   - Add user behavior learning over time

4. **Chatbot Improvements**
   - Integrate NLP models (BERT, GPT) for better understanding
   - Implement conversation memory
   - Add multilingual support

5. **Model Updates**
   - Implement online learning for continuous model updates
   - Add A/B testing for model improvements
   - Implement model versioning

---

## Model Usage Examples

### Predictive Safety Model

```python
from predictive_safety_model import PredictiveSafetyModel

# Initialize model
model = PredictiveSafetyModel()

# Load or train model
model.load_model()  # or model.train_model()

# Predict safety score
safety_score = model.predict_safety_score(
    lat=28.6139, 
    lng=77.2090, 
    timestamp=datetime.now()
)
print(f"Safety Score: {safety_score:.2f}")
```

### Route Optimization

```python
from enhanced_route_optimizer import EnhancedRouteOptimizer

# Initialize optimizer
optimizer = EnhancedRouteOptimizer(safety_model=model)

# Optimize route
route = optimizer.optimize_route_with_safety_scoring(
    start_lat=28.6139,
    start_lng=77.2090,
    end_lat=28.6169,
    end_lng=77.2120
)

print(f"Total Safety Score: {route.total_safety_score}")
print(f"Travel Time: {route.total_travel_time} minutes")
print(f"Route Confidence: {route.route_confidence}")
```

### Anomaly Detection

```python
from dynamic_geofencing import DynamicGeofencing

# Initialize geofencing
geofencing = DynamicGeofencing(safety_model=model)

# Set planned route
geofencing.set_planned_route(route_coordinates)

# Update user location
anomaly_detected = geofencing.update_user_location(
    lat=28.6149,
    lng=77.2100,
    speed=0.0
)

if anomaly_detected:
    status = geofencing.get_current_safety_status()
    print(f"Anomaly detected! Phase: {status['current_phase']}")
```

---

## Conclusion

The Safe Route AI system utilizes a combination of machine learning models, algorithms, and rule-based systems to provide comprehensive safety features. The system is designed to be modular, allowing for easy updates and improvements to individual components.

For questions or contributions, please refer to the main project documentation or contact the development team.

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Maintained By**: Safe Route AI Development Team

