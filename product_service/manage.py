from app import create_app, db
from flask_migrate import MigrateCommand
from flask.cli import with_appcontext
import click
import os
# from services.app.models import Service

app = create_app()

# Додаємо команду для міграцій
@app.cli.command('create_db')
@with_appcontext
def create_db():
    """Створює таблиці в базі даних."""
    db.create_all()

# Міграції через flask
app.cli.add_command(MigrateCommand)
# PORT = 5001
if __name__ == '__main__':
    port = int(os.environ.get('FLASK_RUN_PORT', 5001))
    app.run(host='0.0.0.2', port=port)
    # app.run(host='0.0.0.0', port=5001)
