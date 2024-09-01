from flask import Flask
from .extensions import db
from .routes import main 
def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    with app.app_context():
        app.register_blueprint(main)  # Register the blueprint
        return app
