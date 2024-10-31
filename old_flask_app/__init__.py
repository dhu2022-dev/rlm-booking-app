from flask import Flask

def create_app():
    app = Flask(__name__)
    
    # Import the routes from routes.py
    from .main import main
    
    # Register the routes blueprint
    app.register_blueprint(main)

    if __name__ == "__main__":
        app.run(debug=True)

    return app
