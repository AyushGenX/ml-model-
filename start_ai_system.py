#!/usr/bin/env python3
"""
Startup script for Safe Route AI System
Handles initialization and provides easy startup options
"""

import os
import sys
import subprocess
import time
import signal
from datetime import datetime

def print_banner():
    """Print startup banner"""
    print("=" * 80)
    print("🚀 Safe Route AI System - Predictive Safety & Dynamic Geofencing")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'numpy', 'pandas', 'sklearn', 'flask', 'flask_cors', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} (missing)")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False
    
    print("✓ All dependencies found!")
    return True

def run_tests():
    """Run system tests"""
    print("\n🧪 Running system tests...")
    
    try:
        result = subprocess.run([sys.executable, 'test_ai_system.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✓ All tests passed!")
            return True
        else:
            print("✗ Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Tests timed out")
        return False
    except Exception as e:
        print(f"✗ Test execution failed: {e}")
        return False

def start_ai_server():
    """Start the AI API server"""
    print("\n🚀 Starting AI API server...")
    
    try:
        # Start the Flask server
        process = subprocess.Popen([
            sys.executable, 'enhanced_api_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✓ AI API server started successfully!")
            print("📍 Server running at: http://localhost:5000")
            print("🔗 Health check: http://localhost:5000/health")
            return process
        else:
            stdout, stderr = process.communicate()
            print("✗ Failed to start AI server:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"✗ Failed to start AI server: {e}")
        return None

def start_node_server():
    """Start the Node.js server"""
    print("\n🚀 Starting Node.js server...")
    
    try:
        # Check if package.json exists
        if not os.path.exists('package.json'):
            print("✗ package.json not found. Make sure you're in the project root.")
            return None
        
        # Start Node.js server (Windows compatible)
        try:
            if os.name == 'nt':  # Windows
                # Try different approaches for Windows
                try:
                    process = subprocess.Popen([
                        'npm', 'start'
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                except:
                    process = subprocess.Popen([
                        'cmd', '/c', 'npm', 'start'
                    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:  # Unix/Linux/Mac
                process = subprocess.Popen([
                    'npm', 'start'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"✗ Failed to start Node.js server: {e}")
            return None
        
        # Wait a moment for server to start
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            print("✓ Node.js server started successfully!")
            print("📍 Server running at: http://localhost:8080")
            return process
        else:
            stdout, stderr = process.communicate()
            print("✗ Failed to start Node.js server:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"✗ Failed to start Node.js server: {e}")
        return None

def show_usage_info():
    """Show usage information"""
    print("\n" + "=" * 80)
    print("📖 Usage Information")
    print("=" * 80)
    print("""
🎯 API Endpoints:
   • POST /api/plan-safe-route     - Plan AI-optimized safe route
   • POST /api/update-location     - Update user location
   • POST /api/sakha-chat          - Chat with Sakha assistant
   • GET  /api/safety-status/<id>  - Get safety status
   • GET  /health                  - Health check

🔧 Integration:
   • AI API Server:    http://localhost:5000
   • Node.js Server:   http://localhost:8080
   • Combined System:  Use both servers together

📱 Frontend Integration:
   • Update your existing frontend to call AI endpoints
   • Add real-time location tracking
   • Integrate Sakha chatbot UI

🧪 Testing:
   • Run tests: python test_ai_system.py
   • Test API: curl http://localhost:5000/health
   • Full system test: python pythonScript/safe_route_ai_system.py

📚 Documentation:
   • See AI_FEATURES_README.md for detailed documentation
   • Check individual Python files for code examples
""")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print("\n\n🛑 Shutting down Safe Route AI System...")
    sys.exit(0)

def main():
    """Main startup function"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies first.")
        return False
    
    # Ask user what they want to do
    print("\n" + "=" * 80)
    print("🚀 Startup Options:")
    print("=" * 80)
    print("1. Run tests only")
    print("2. Start AI server only")
    print("3. Start both AI and Node.js servers")
    print("4. Show usage information")
    print("5. Exit")
    
    try:
        choice = input("\nSelect option (1-5): ").strip()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return True
    
    if choice == "1":
        # Run tests only
        if run_tests():
            print("\n✅ All tests passed! System is ready.")
        else:
            print("\n❌ Some tests failed. Please check the errors.")
        return True
        
    elif choice == "2":
        # Start AI server only
        ai_process = start_ai_server()
        if ai_process:
            print("\n✅ AI server is running!")
            print("Press Ctrl+C to stop the server.")
            try:
                ai_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping AI server...")
                ai_process.terminate()
        return True
        
    elif choice == "3":
        # Start both servers
        ai_process = start_ai_server()
        if not ai_process:
            print("❌ Cannot start Node.js server without AI server.")
            return False
        
        node_process = start_node_server()
        if not node_process:
            print("❌ Node.js server failed to start.")
            ai_process.terminate()
            return False
        
        print("\n✅ Both servers are running!")
        print("📍 AI API Server: http://localhost:5000")
        print("📍 Node.js Server: http://localhost:8080")
        print("Press Ctrl+C to stop both servers.")
        
        try:
            # Wait for either process to exit
            while True:
                if ai_process.poll() is not None:
                    print("❌ AI server stopped unexpectedly.")
                    break
                if node_process.poll() is not None:
                    print("❌ Node.js server stopped unexpectedly.")
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping both servers...")
            ai_process.terminate()
            node_process.terminate()
        
        return True
        
    elif choice == "4":
        # Show usage information
        show_usage_info()
        return True
        
    elif choice == "5":
        # Exit
        print("👋 Goodbye!")
        return True
        
    else:
        print("❌ Invalid option. Please select 1-5.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
