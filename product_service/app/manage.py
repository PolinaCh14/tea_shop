from app import create_app
from app.extensions import db
from flask_migrate import MigrateCommand
from flask.cli import with_appcontext
import click

app = create_app()

# Add the 'create_db' command for migrations
@app.cli.command('create_db')
@with_appcontext
def create_db():
    """Create tables in the database."""
    db.create_all()

# Add the flask-migrate command
app.cli.add_command(MigrateCommand)

if __name__ == '__main__':
    app.run()
