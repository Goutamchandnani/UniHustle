from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
# Celery will be initialized with app context later
from celery import Celery
celery = Celery()
from flask_jwt_extended import JWTManager
jwt = JWTManager()
