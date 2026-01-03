import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')
    
    from celery.schedules import crontab
    CELERYBEAT_SCHEDULE = {
        'scrape-every-hour': {
            'task': 'app.tasks.scrape_jobs_task',
            'schedule': crontab(minute=0), # Every hour
        },
        'cleanup-daily': {
            'task': 'app.tasks.cleanup_old_jobs_task',
            'schedule': crontab(hour=0, minute=0), # Midnight
        },
    }
    
    # Scraper Keys
    REED_API_KEY = os.environ.get('REED_API_KEY')

class DevelopmentConfig(Config):
    DEBUG = True
    CELERY_TASK_ALWAYS_EAGER = True # Run tasks synchronously for local dev (no redis needed)

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
