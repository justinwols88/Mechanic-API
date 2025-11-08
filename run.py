from application import create_app

app = create_app()
print(f"App type: {type(app)}")
print(f"App is None: {app is None}")

if app is not None and __name__ == '__main__':
    app.run(debug=True)
else:
    print("ERROR: app is None!")