from app import create_app, db
from flask_migrate import MigrateCommand
from flask.cli import with_appcontext
import click

app = create_app()

# Додаємо команду для міграцій
@app.cli.command('create_db')
@with_appcontext
def create_db():
    """Створює таблиці в базі даних."""
    db.create_all()

# Міграції через flask
app.cli.add_command(MigrateCommand)

if __name__ == '__main__':
    app.run()
