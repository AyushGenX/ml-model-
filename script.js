// Safe Route AI Frontend JavaScript
class SafeRouteApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:5000';
        this.currentRoute = null;
        this.isNavigating = false;
        this.map = null;
        this.routePolyline = null;
        this.userMarker = null;
        this.userPosition = null;
        this.geoWatchId = null;
        this.safetyPollId = null;
        this.routePollId = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSystemStatus();
        this.setupNavigation();
        this.setupChat();
        this.setupSettings();
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showSection(link.getAttribute('href').substring(1));
            });
        });

        // Route form
        document.getElementById('routeForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.planRoute();
        });

        // Navigation buttons
        document.getElementById('startNavigation').addEventListener('click', () => {
            this.startNavigation();
        });

        document.getElementById('shareRoute').addEventListener('click', () => {
            this.shareRoute();
        });

        // Chat form
        document.getElementById('chatForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendChatMessage();
        });

        // Settings
        document.getElementById('safetyThreshold').addEventListener('input', (e) => {
            document.getElementById('thresholdValue').textContent = e.target.value;
        });
    }

    setupNavigation() {
        // Mobile navigation toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
    }

    setupChat() {
        // Auto-scroll chat to bottom
        const chatMessages = document.getElementById('chatMessages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    setupSettings() {
        // Load saved settings
        const savedThreshold = localStorage.getItem('safetyThreshold');
        if (savedThreshold) {
            document.getElementById('safetyThreshold').value = savedThreshold;
            document.getElementById('thresholdValue').textContent = savedThreshold;
        }

        // Save settings on change
        document.getElementById('safetyThreshold').addEventListener('change', (e) => {
            localStorage.setItem('safetyThreshold', e.target.value);
        });
    }

    showSection(sectionId) {
        // Hide all sections
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        // Show selected section
        document.getElementById(sectionId).classList.add('active');

        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[href="#${sectionId}"]`).classList.add('active');

        // Load section-specific data
        if (sectionId === 'safety') {
            this.loadSafetyStatus();
            this.startSafetyMonitoring();
        }
    }

    async loadSystemStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const data = await response.json();
            
            if (data.status === 'healthy') {
                document.getElementById('activeRoutes').textContent = data.system_status.active_routes;
                document.getElementById('safetyLevel').textContent = 'Normal';
                document.getElementById('systemUptime').textContent = this.formatUptime(data.system_status.system_uptime);
            }
        } catch (error) {
            console.error('Failed to load system status:', error);
            this.showToast('Failed to load system status', 'error');
        }
    }

    async loadSafetyStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/safety-status/frontend_user`);
            const data = await response.json();
            
            if (data.success) {
                const safetyScore = data.safety_score || 45; // Default safe score
                const phase = data.phase || 'normal';
                
                // Update safety indicator
                const indicator = document.getElementById('safetyIndicator');
                const statusText = document.getElementById('safetyStatusText');
                const progressFill = document.getElementById('safetyProgress');
                const scoreValue = document.getElementById('safetyScoreValue');
                
                statusText.textContent = phase.charAt(0).toUpperCase() + phase.slice(1);
                scoreValue.textContent = Math.round(safetyScore);
                progressFill.style.width = `${Math.min(safetyScore, 100)}%`;
                
                // Update status circle color based on safety score
                const statusCircle = indicator.querySelector('.status-circle');
                if (safetyScore < 30) {
                    statusCircle.style.background = '#28a745'; // Green
                } else if (safetyScore < 70) {
                    statusCircle.style.background = '#ffc107'; // Yellow
                } else {
                    statusCircle.style.background = '#dc3545'; // Red
                }
            } else {
                // Show default safety status if API fails
                this.showDefaultSafetyStatus();
            }
        } catch (error) {
            console.error('Failed to load safety status:', error);
            // Show default safety status on error
            this.showDefaultSafetyStatus();
        }
    }

    showDefaultSafetyStatus() {
        // Set default safety values
        const statusText = document.getElementById('safetyStatusText');
        const progressFill = document.getElementById('safetyProgress');
        const scoreValue = document.getElementById('safetyScoreValue');
        const statusCircle = document.querySelector('.status-circle');
        
        statusText.textContent = 'Normal';
        scoreValue.textContent = '45';
        progressFill.style.width = '45%';
        statusCircle.style.background = '#ffc107'; // Yellow for moderate safety
    }

    startSafetyMonitoring() {
        // Add safety alerts and tips
        this.addSafetyAlerts();
        this.addSafetyTips();
    }

    addSafetyAlerts() {
        // Create safety alerts section
        const safetyFeatures = document.querySelector('.safety-features');
        if (safetyFeatures) {
            const alertsSection = document.createElement('div');
            alertsSection.className = 'safety-alerts';
            alertsSection.innerHTML = `
                <h3>Safety Alerts</h3>
                <div class="alert-list">
                    <div class="alert-item safe">
                        <i class="fas fa-check-circle"></i>
                        <span>Location tracking active</span>
                    </div>
                    <div class="alert-item safe">
                        <i class="fas fa-shield-alt"></i>
                        <span>Emergency contacts configured</span>
                    </div>
                    <div class="alert-item warning">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Avoid isolated areas after dark</span>
                    </div>
                </div>
            `;
            safetyFeatures.appendChild(alertsSection);
        }
    }

    addSafetyTips() {
        // Add dynamic safety tips
        const safetyFeatures = document.querySelector('.safety-features');
        if (safetyFeatures) {
            const tipsSection = document.createElement('div');
            tipsSection.className = 'safety-tips';
            tipsSection.innerHTML = `
                <h3>Safety Tips</h3>
                <div class="tips-list">
                    <div class="tip-item">
                        <i class="fas fa-lightbulb"></i>
                        <span>Share your live location with trusted contacts</span>
                    </div>
                    <div class="tip-item">
                        <i class="fas fa-phone"></i>
                        <span>Keep emergency numbers on speed dial</span>
                    </div>
                    <div class="tip-item">
                        <i class="fas fa-users"></i>
                        <span>Travel with companions when possible</span>
                    </div>
                    <div class="tip-item">
                        <i class="fas fa-eye"></i>
                        <span>Stay aware of your surroundings</span>
                    </div>
                </div>
            `;
            safetyFeatures.appendChild(tipsSection);
        }
    }

    async planRoute() {
        const startLocation = document.getElementById('startLocation').value;
        const endLocation = document.getElementById('endLocation').value;
        const travelMode = document.getElementById('travelMode').value;

        if (!startLocation || !endLocation) {
            this.showToast('Please enter both start and end locations', 'warning');
            return;
        }

        this.showLoading(true);

        try {
            // Get coordinates for start and end locations
            const startCoords = await this.geocodeLocation(startLocation);
            const endCoords = await this.geocodeLocation(endLocation);

            if (!startCoords || !endCoords) {
                this.showToast('Could not find coordinates for the specified locations', 'error');
                return;
            }

            const response = await fetch(`${this.apiBaseUrl}/api/plan-safe-route`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    source: startCoords,
                    destination: endCoords,
                    user_id: 'frontend_user',
                    travel_mode: travelMode
                })
            });

            const data = await response.json();

            if (data.success) {
                this.currentRoute = data.data;
                this.displayRouteResults(data.data);
                this.showToast('Route planned successfully!', 'success');
            } else {
                this.showToast(data.error || data.message || 'Failed to plan route', 'error');
            }
        } catch (error) {
            console.error('Route planning failed:', error);
            this.showToast('Failed to plan route. Please try again.', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayRouteResults(route) {
        document.getElementById('travelTime').textContent = `${Math.round(route.total_travel_time)} minutes`;
        document.getElementById('safetyScore').textContent = Math.round(route.total_safety_score);
        document.getElementById('routeConfidence').textContent = `${Math.round(route.route_confidence * 100)}%`;
        
        document.getElementById('routeResults').classList.remove('hidden');
        document.getElementById('routeResults').scrollIntoView({ behavior: 'smooth' });
        
        // Show and initialize map
        this.showRouteMap(route);
    }

    startNavigation() {
        if (!this.currentRoute) {
            this.showToast('No route selected', 'warning');
            return;
        }

        this.isNavigating = true;
        this.showToast('Navigation started! Stay safe on your journey.', 'success');
        
        // Show navigation interface
        this.showNavigationInterface();
        
        // Begin real-time features
        this.startLocationWatch();
        this.startSafetyPolling();
        this.startRoutePolling();
    }

    showNavigationInterface() {
        // Create navigation overlay
        const navOverlay = document.createElement('div');
        navOverlay.id = 'navigationOverlay';
        navOverlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            z-index: 10000;
            display: flex;
            flex-direction: column;
            color: white;
            padding: 20px;
        `;
        
        navOverlay.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h2>🚗 Navigation Active</h2>
                <button id="stopNavigation" style="background: #dc3545; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    Stop Navigation
                </button>
            </div>
            <div id="navInstructions" style="flex: 1; background: rgba(255, 255, 255, 0.1); padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3>Next: Continue straight for 2.5 km</h3>
                <p>Turn right at the traffic light</p>
            </div>
            <div style="display: flex; gap: 10px;">
                <button id="recenterMap" style="background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    Recenter Map
                </button>
                <button id="toggleMute" style="background: #6c757d; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    Mute
                </button>
            </div>
        `;
        
        document.body.appendChild(navOverlay);
        
        // Add event listeners
        document.getElementById('stopNavigation').addEventListener('click', () => {
            this.stopNavigation();
        });
        
        document.getElementById('recenterMap').addEventListener('click', () => {
            if (this.map) {
                this.map.invalidateSize();
            }
        });
    }

    stopNavigation() {
        this.isNavigating = false;
        const navOverlay = document.getElementById('navigationOverlay');
        if (navOverlay) {
            navOverlay.remove();
        }
        this.showToast('Navigation stopped', 'info');

        // Stop realtime timers/watchers
        if (this.geoWatchId !== null) {
            navigator.geolocation && navigator.geolocation.clearWatch(this.geoWatchId);
            this.geoWatchId = null;
        }
        if (this.safetyPollId) {
            clearInterval(this.safetyPollId);
            this.safetyPollId = null;
        }
        if (this.routePollId) {
            clearInterval(this.routePollId);
            this.routePollId = null;
        }
    }

    startLocationWatch() {
        if (!('geolocation' in navigator)) {
            // Fallback to simulated updates
            this.showToast('Geolocation not available. Using simulated location.', 'warning');
            this.startSimulatedLocationUpdates();
            return;
        }

        this.geoWatchId = navigator.geolocation.watchPosition(
            async ({ coords }) => {
                if (!this.isNavigating) return;
                const { latitude, longitude } = coords;
                this.userPosition = { lat: latitude, lng: longitude };
                this.updateUserMarker();
                await this.updateLocation(latitude, longitude);
            },
            (err) => {
                console.warn('Geolocation error:', err);
                this.startSimulatedLocationUpdates();
            },
            { enableHighAccuracy: true, maximumAge: 5000, timeout: 10000 }
        );
    }

    startSimulatedLocationUpdates() {
        if (!this.isNavigating) return;
        // Simulate around Delhi
        const tick = async () => {
            if (!this.isNavigating) return;
            const latitude = 28.6139 + (Math.random() - 0.5) * 0.01;
            const longitude = 77.2090 + (Math.random() - 0.5) * 0.01;
            this.userPosition = { lat: latitude, lng: longitude };
            this.updateUserMarker();
            await this.updateLocation(latitude, longitude);
        };
        tick();
        this.geoSimId = setInterval(tick, 15000);
    }

    async updateLocation(latitude, longitude) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/update-location`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'frontend_user',
                    latitude: latitude ?? 28.6139,
                    longitude: longitude ?? 77.2090,
                    timestamp: new Date().toISOString()
                })
            });

            const data = await response.json();
            
            if (data.anomaly_detected) {
                this.showToast('Anomaly detected! Please stay alert.', 'warning');
            }
        } catch (error) {
            console.error('Location update failed:', error);
        }
    }

    startSafetyPolling() {
        // Update safety widgets every 15s
        if (this.safetyPollId) clearInterval(this.safetyPollId);
        const poll = async () => {
            await this.loadSafetyStatus();
        };
        poll();
        this.safetyPollId = setInterval(poll, 15000);
    }

    startRoutePolling() {
        if (this.routePollId) clearInterval(this.routePollId);
        const poll = async () => {
            if (!this.isNavigating || !this.currentRoute) return;
            const endWaypoint = this.currentRoute.waypoints?.[this.currentRoute.waypoints.length - 1];
            if (!endWaypoint) return;
            const origin = this.userPosition || { lat: this.currentRoute.waypoints[0].lat, lng: this.currentRoute.waypoints[0].lng };

            try {
                const response = await fetch(`${this.apiBaseUrl}/api/plan-safe-route`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        source: { lat: origin.lat, lng: origin.lng },
                        destination: { lat: endWaypoint.lat, lng: endWaypoint.lng },
                        user_id: 'frontend_user',
                        travel_mode: document.getElementById('travelMode').value
                    })
                });
                const data = await response.json();
                if (data.success) {
                    this.currentRoute = data.data;
                    this.updateRouteUIAndMap(this.currentRoute);
                }
            } catch (e) {
                console.warn('Route polling failed', e);
            }
        };
        poll();
        this.routePollId = setInterval(poll, 20000);
    }

    updateRouteUIAndMap(route) {
        // Update UI
        document.getElementById('travelTime').textContent = `${Math.round(route.total_travel_time)} minutes`;
        document.getElementById('safetyScore').textContent = Math.round(route.total_safety_score);
        document.getElementById('routeConfidence').textContent = `${Math.round(route.route_confidence * 100)}%`;
        // Update map polyline
        this.showRouteMap(route);
    }

    shareRoute() {
        if (!this.currentRoute) {
            this.showToast('No route to share', 'warning');
            return;
        }

        const routeData = {
            start: document.getElementById('startLocation').value,
            end: document.getElementById('endLocation').value,
            travelTime: this.currentRoute.travel_time,
            safetyScore: this.currentRoute.safety_score
        };

        if (navigator.share) {
            navigator.share({
                title: 'Safe Route',
                text: `Safe route from ${routeData.start} to ${routeData.end}`,
                url: window.location.href
            });
        } else {
            // Fallback: copy to clipboard
            const text = `Safe Route: ${routeData.start} → ${routeData.end}\nTravel Time: ${routeData.travelTime} minutes\nSafety Score: ${routeData.safetyScore}`;
            navigator.clipboard.writeText(text).then(() => {
                this.showToast('Route details copied to clipboard', 'success');
            });
        }
    }

    async sendChatMessage() {
        const input = document.getElementById('chatInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');
        input.value = '';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            const response = await fetch(`${this.apiBaseUrl}/api/sakha-chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'frontend_user',
                    message: message
                })
            });

            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            // Add bot response
            const responseText = data.data?.response || data.data?.message || 'I apologize, but I cannot process your request at the moment.';
            this.addChatMessage(responseText, 'bot');
        } catch (error) {
            console.error('Chat failed:', error);
            this.hideTypingIndicator();
            this.addChatMessage('I apologize, but I cannot process your request at the moment. Please try again later.', 'bot');
        }
    }

    addChatMessage(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.innerHTML = sender === 'bot' ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = `<p>${message}</p>`;
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chatMessages');
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot-message typing-indicator';
        typingDiv.id = 'typing-indicator';
        
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Sakha is typing...</p>
            </div>
        `;
        
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (show) {
            overlay.classList.add('show');
        } else {
            overlay.classList.remove('show');
        }
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    formatUptime(uptime) {
        const date = new Date(uptime);
        const now = new Date();
        const diff = now - date;
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        return `${hours}h ${minutes}m`;
    }

    async geocodeLocation(locationName) {
        try {
            // Use OpenStreetMap Nominatim API for geocoding (free)
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(locationName)}&limit=1`);
            const data = await response.json();
            
            if (data && data.length > 0) {
                return {
                    lat: parseFloat(data[0].lat),
                    lng: parseFloat(data[0].lon)
                };
            }
            return null;
        } catch (error) {
            console.error('Geocoding failed:', error);
            return null;
        }
    }

    showRouteMap(route) {
        // Show map container
        document.getElementById('routeMap').style.display = 'block';
        
        // Initialize map if not already done
        if (!this.map) {
            this.map = L.map('map').setView([28.6139, 77.2090], 13);
            
            // Add OpenStreetMap tiles
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);
        }
        
        // Clear previous route
        if (this.routePolyline) {
            this.map.removeLayer(this.routePolyline);
        }
        
        // Add route waypoints if available
        if (route.waypoints && route.waypoints.length > 0) {
            const waypoints = route.waypoints.map(wp => [wp.lat, wp.lng]);
            
            // Add start marker
            const startMarker = L.marker(waypoints[0]).addTo(this.map);
            startMarker.bindPopup('<b>Start</b>').openPopup();
            
            // Add end marker
            const endMarker = L.marker(waypoints[waypoints.length - 1]).addTo(this.map);
            endMarker.bindPopup('<b>Destination</b>');
            
            // Add route polyline
            this.routePolyline = L.polyline(waypoints, {
                color: '#667eea',
                weight: 4,
                opacity: 0.8
            }).addTo(this.map);
            
            // Fit map to route
            this.map.fitBounds(this.routePolyline.getBounds());
        } else {
            // Fallback: show a simple route line
            const startCoords = [28.6139, 77.2090]; // Delhi
            const endCoords = [28.5355, 77.3910];
            
            L.marker(startCoords).addTo(this.map).bindPopup('Start');
            L.marker(endCoords).addTo(this.map).bindPopup('Destination');
            L.polyline([startCoords, endCoords], {color: '#667eea', weight: 4}).addTo(this.map);
            this.map.fitBounds([[28.5, 77.1], [28.7, 77.5]]);
        }

        // Ensure user marker shown if we have position
        this.updateUserMarker();
    }

    updateUserMarker() {
        if (!this.map || !this.userPosition) return;
        const { lat, lng } = this.userPosition;
        if (!this.userMarker) {
            this.userMarker = L.marker([lat, lng], {
                icon: L.icon({
                    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
                    iconSize: [25, 41],
                    iconAnchor: [12, 41]
                })
            }).addTo(this.map);
            this.userMarker.bindPopup('<b>You</b>');
        } else {
            this.userMarker.setLatLng([lat, lng]);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SafeRouteApp();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
