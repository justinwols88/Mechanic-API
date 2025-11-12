from application import create_app, db 
def test_route_directly():
            
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Push application context
    ctx = app.app_context()
    ctx.push()
    
    try:
        db.create_all()
        # Your test code here
    finally:
        db.drop_all()
        ctx.pop()