# check_database.py
import sqlite3
import os

def check_database():
    db_path = 'mechanics.db'
    
    if os.path.exists(db_path):
        print(f"✅ Database file found: {db_path}")
        print(f"📊 File size: {os.path.getsize(db_path)} bytes")
        
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Tables in database:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            print(f"   - {table_name} ({count} rows)")
            
        conn.close()
        
        # Test sample data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM customers;")
        customers = cursor.fetchall()
        
        print("\n👥 Sample customers:")
        for customer in customers:
            print(f"   - {customer[0]} ({customer[1]})")
            
        conn.close()
        
    else:
        print("❌ Database file not found")

if __name__ == '__main__':
    check_database()