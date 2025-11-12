from application import create_app, db

# Create the database and load test data
app = create_app()
client = app.test_client()

# Test customer login
print("=== Testing Customer Login ===")
response = client.post('/customers/login',
                      json={'email': 'test@example.com'},  # Try without password
                      content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")

# Test mechanic login
print("\n=== Testing Mechanic Login ===")
response = client.post('/mechanic/login',
                      json={'email': 'mechanic@example.com'},  # Try without password
                      content_type='application/json')
print(f"Status: {response.status_code}")
print(f"Response: {response.get_json()}")