from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
from app.extensions import db, ma
from app.config import Config
from app.routes import service_blueprint
from app.extensions import db

# db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config.from_object(Config)

    db.init_app(app)
    # migrate.init_app(app, db)

    app.register_blueprint(service_blueprint)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'


    return app
