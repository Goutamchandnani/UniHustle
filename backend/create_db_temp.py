import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def create_db():
    db_url = os.getenv('DATABASE_URL')
    if not db_url or 'sqlite' in db_url:
        print("Error: DATABASE_URL is not set to PostgreSQL")
        return False

    result = urlparse(db_url)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    
    print(f"Connecting to PostgreSQL at {hostname}:{port} as {username}...")

    try:
        # Connect to 'postgres' system db
        con = psycopg2.connect(
            dbname='postgres',
            user=username,
            password=password,
            host=hostname,
            port=port
        )
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = con.cursor()
        
        # Check if db exists
        cur.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database}'")
        exists = cur.fetchone()
        
        if not exists:
            print(f"Database '{database}' does not exist. Creating...")
            cur.execute(f"CREATE DATABASE {database};")
            print(f"Database '{database}' created successfully.")
        else:
            print(f"Database '{database}' already exists.")
            
        cur.close()
        con.close()
        return True
        
    except Exception as e:
        print(f"\nConnection failed: {e}")
        return False

if __name__ == "__main__":
    if create_db():
        print("SUCCESS")
    else:
        print("FAILURE")
