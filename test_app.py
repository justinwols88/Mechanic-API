from application import create_app

app = create_app()

if __name__ == '__main__':
    print("🚀 Starting Mechanic API...")
    print("📊 Database: mechanics.db")
    print("🌐 API Base URL: http://localhost:5000")
    print("📚 Available Endpoints:")
    print("   GET  /customers/")
    print("   POST /customers/login")
    print("   GET  /customers/my-tickets (requires token)")
    print("   GET  /mechanics/")
    print("   POST /mechanics/login") 
    print("   GET  /mechanics/leaderboard")
    print("   GET  /service-tickets/")
    print("   GET  /inventory/")
    print("\n💡 Run 'python setup_database.py' first to initialize the database")
    app.run(debug=True, host='0.0.0.0', port=5000)