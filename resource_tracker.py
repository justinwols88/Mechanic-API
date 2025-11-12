# enhanced_tracer.py
import tracemalloc
import gc
import sqlite3
import sys
from application import create_app
from application.extensions import db

# Global list to track all connections
all_connections = []

# Store original connect function
original_connect = sqlite3.connect

def traced_connect(*args, **kwargs):
    """Wrapper to track SQLite connections"""
    conn = original_connect(*args, **kwargs)
    
    # Capture stack trace
    import traceback
    stack = traceback.extract_stack()
    
    connection_info = {
        'connection': conn,
        'stack': stack,
        'args': args,
        'kwargs': kwargs
    }
    all_connections.append(connection_info)
    
    print(f"🔗 SQLite connection created: {len(all_connections)}")
    for frame in stack[-3:]:  # Show last 3 frames
        print(f"   {frame.filename}:{frame.lineno} in {frame.name}")
    
    # Track when connection is closed
    original_close = conn.close
    def traced_close():
        print(f"✅ SQLite connection closed: {len(all_connections)}")
        all_connections.remove(connection_info)
        original_close()
    
    conn.close = traced_close
    return conn

# Apply the monkey patch
sqlite3.connect = traced_connect

def test_inventory_creation():
    """Test inventory creation with enhanced tracing"""
    tracemalloc.start()
    
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True  # Show all SQL
    
    with app.app_context():
        print("=== Creating database tables ===")
        db.create_all()
        
        client = app.test_client()
        
        # Test data that should work
        new_item = {
            'name': 'Test Air Filter',
            'category': 'filters',
            'quantity': 25,
            'price': 15.99,
            'min_stock_level': 10
        }
        
        print(f"\n=== Before POST request - Connections: {len(all_connections)} ===")
        
        # Make the request
        response = client.post('/inventory/',
                             json=new_item,
                             content_type='application/json')
        
        print(f"\n=== After POST request ===")
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.get_data(as_text=True)}")
        print(f"Active connections: {len(all_connections)}")
        
        # Check if item was created
        if response.status_code == 201:
            print("✅ Item created successfully")
        else:
            print("❌ Item creation failed")
            # Try to get more error details
            try:
                error_data = response.get_json()
                print(f"Error details: {error_data}")
            except:
                print("No JSON error response")
        
        # Force cleanup
        print("\n=== Cleaning up ===")
        db.session.close()
        db.session.remove()
        db.drop_all()
        
        # Force garbage collection
        gc.collect()
        
        print(f"Remaining connections after cleanup: {len(all_connections)}")
        
        # Show unclosed connections
        if all_connections:
            print("\n=== UNCLOSED CONNECTIONS ===")
            for i, conn_info in enumerate(all_connections):
                print(f"Connection {i+1}:")
                for frame in conn_info['stack'][-5:]:
                    print(f"  {frame.filename}:{frame.lineno} in {frame.name}")
    
    # Memory analysis
    snapshot = tracemalloc.take_snapshot()
    print("\n=== MEMORY ANALYSIS ===")
    
    # Look for SQLite-related allocations
    for stat in snapshot.statistics('lineno')[:15]:
        if 'sqlite' in str(stat).lower() or 'sqlalchemy' in str(stat).lower():
            print(f"SQL-related: {stat}")
    
    tracemalloc.stop()

if __name__ == '__main__':
    test_inventory_creation()