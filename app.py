# app.py - Main application entry point
from application import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Mechanic API...")
    print("📊 Database: mechanics.db")
    print("🌐 API Base URL: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)