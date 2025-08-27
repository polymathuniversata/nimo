import traceback

try:
    import app
    app_instance = app.create_app()
    print("App created successfully!")
except Exception as e:
    traceback.print_exc()
    print("Error occurred:", str(e))