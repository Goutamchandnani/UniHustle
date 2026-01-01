import os
from app import create_app, db
from app.models import * # Import all models so alembic can detect them

app = create_app(os.getenv('FLASK_ENV') or 'default')

if __name__ == '__main__':
    app.run()
