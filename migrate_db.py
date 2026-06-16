import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app import create_app
from models.db import db

load_dotenv()

def migrate():
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable is not set.")
        return

    print("Connecting to Supabase and verifying tables...")
    # creating the app automatically triggers db.create_all() for Supabase
    app = create_app()

    sqlite_uri = 'sqlite:///jaundice_tracker.db'
    sqlite_engine = create_engine(sqlite_uri)
    
    with app.app_context():
        pg_engine = db.engine
        
        print("Migrating data...")
        # Delete existing data in target to avoid duplicates
        with pg_engine.begin() as pg_conn:
            for table in reversed(db.metadata.sorted_tables):
                pg_conn.execute(table.delete())
        
        with sqlite_engine.connect() as sqlite_conn:
            with pg_engine.begin() as pg_conn:
                for table in db.metadata.sorted_tables:
                    print(f"  -> Copying table: {table.name}")
                    records = sqlite_conn.execute(table.select()).fetchall()
                    if records:
                        data_to_insert = [dict(row._mapping) for row in records]
                        pg_conn.execute(table.insert(), data_to_insert)
                        print(f"     Copied {len(records)} rows.")
                    else:
                        print("     Table is empty.")

    print("\nMigration complete! Your local data is now in Supabase.")
    print("You can now safely redeploy.")

if __name__ == "__main__":
    migrate()
