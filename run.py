from app import create_app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # If you need to create tables, do it here within the context
        # But typically you should use migrations instead
        # db.create_all()
        app.run(debug=True)