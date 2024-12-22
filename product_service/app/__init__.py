from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.extensions import db, migrate, ma
from app.config import Config
from app.routes import product_blueprint
from app.extensions import db, migrate
# from ..app.models import Service

# db = SQLAlchemy()
# migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(product_blueprint)

    @app.route('/test/')
    def test_page():
        return '<h1>Testing the Flask Application Factory Pattern</h1>'
    
    # app.run(host='0.0.0.0', port=5001)

    return app
