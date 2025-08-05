#!/usr/bin/env python3
"""
Migration script to transfer OCT data from local PostgreSQL to Supabase
"""
import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_data():
    """Extract data from local PostgreSQL database"""
    local_db_params = {
        'host': 'localhost',
        'port': 5432,
        'user': 'oct_user',
        'password': 'oct_password',
        'database': 'oct_poc'
    }
    
    try:
        conn = psycopg2.connect(**local_db_params)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM h1_carry_over_performance ORDER BY id")
        carry_over_data = cursor.fetchall()
        carry_over_columns = [desc[0] for desc in cursor.description]
        
        cursor.execute("SELECT * FROM h1_collections_performance ORDER BY id")
        collections_data = cursor.fetchall()
        collections_columns = [desc[0] for desc in cursor.description]
        
        cursor.close()
        conn.close()
        
        return {
            'carry_over': {
                'columns': carry_over_columns,
                'data': carry_over_data
            },
            'collections': {
                'columns': collections_columns,
                'data': collections_data
            }
        }
        
    except Exception as e:
        logger.error(f"Error extracting local data: {e}")
        raise

def create_supabase_tables(supabase_url):
    """Create tables in Supabase database"""
    try:
        conn = psycopg2.connect(supabase_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS h1_carry_over_performance (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(100) NOT NULL,
                period VARCHAR(20) NOT NULL,
                units_transferred INTEGER,
                revenue NUMERIC(12,2),
                gross_profit NUMERIC(12,2),
                taxes_and_surcharges NUMERIC(12,2),
                period_expenses NUMERIC(12,2),
                net_profit NUMERIC(12,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_carry_over_period ON h1_carry_over_performance(period);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_carry_over_project ON h1_carry_over_performance(project_name);")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS h1_collections_performance (
                id SERIAL PRIMARY KEY,
                project_name VARCHAR(100) NOT NULL,
                annual_target NUMERIC(12,2),
                h1_budget NUMERIC(12,2),
                h1_actual NUMERIC(12,2),
                h1_completion_rate VARCHAR(10),
                annual_completion_rate VARCHAR(10),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_collections_project ON h1_collections_performance(project_name);")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Supabase tables created successfully")
        
    except Exception as e:
        logger.error(f"Error creating Supabase tables: {e}")
        raise

def migrate_data(supabase_url, local_data):
    """Migrate data to Supabase"""
    try:
        conn = psycopg2.connect(supabase_url)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM h1_carry_over_performance")
        cursor.execute("DELETE FROM h1_collections_performance")
        
        carry_over_columns = local_data['carry_over']['columns']
        for row in local_data['carry_over']['data']:
            placeholders = ','.join(['%s'] * len(row))
            columns_str = ','.join(carry_over_columns)
            cursor.execute(
                f"INSERT INTO h1_carry_over_performance ({columns_str}) VALUES ({placeholders})",
                row
            )
        
        collections_columns = local_data['collections']['columns']
        for row in local_data['collections']['data']:
            placeholders = ','.join(['%s'] * len(row))
            columns_str = ','.join(collections_columns)
            cursor.execute(
                f"INSERT INTO h1_collections_performance ({columns_str}) VALUES ({placeholders})",
                row
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Data migration completed successfully")
        
    except Exception as e:
        logger.error(f"Error migrating data: {e}")
        raise

def verify_migration(supabase_url):
    """Verify the migration was successful"""
    try:
        conn = psycopg2.connect(supabase_url)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM h1_carry_over_performance")
        carry_over_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM h1_collections_performance")
        collections_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        logger.info(f"Migration verification:")
        logger.info(f"  h1_carry_over_performance: {carry_over_count} records")
        logger.info(f"  h1_collections_performance: {collections_count} records")
        
        return carry_over_count, collections_count
        
    except Exception as e:
        logger.error(f"Error verifying migration: {e}")
        raise

def main():
    """Main migration function"""
    supabase_url = os.getenv('SUPABASE_DATABASE_URL')
    if not supabase_url:
        logger.error("SUPABASE_DATABASE_URL environment variable not set")
        return
    
    try:
        logger.info("Starting OCT data migration to Supabase...")
        
        logger.info("Extracting data from local PostgreSQL...")
        local_data = get_local_data()
        
        logger.info("Creating tables in Supabase...")
        create_supabase_tables(supabase_url)
        
        logger.info("Migrating data to Supabase...")
        migrate_data(supabase_url, local_data)
        
        logger.info("Verifying migration...")
        verify_migration(supabase_url)
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    main()
