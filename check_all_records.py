import os
import psycopg2
import json

def check_all_records():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    # Get all tables
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    tables = [row[0] for row in cur.fetchall()]

    print('All Records in Database:')
    print('=' * 60)

    for table in sorted(tables):
        print(f'\nTable: {table}')
        print('-' * 40)
        
        # Get column names first
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table,))
        
        columns = [row[0] for row in cur.fetchall()]
        
        # Get all records
        cur.execute(f"SELECT * FROM {table}")
        records = cur.fetchall()
        
        if not records:
            print("  (No records)")
            continue
            
        print(f"  Found {len(records)} record(s)")
        print()
        
        # Print column headers
        print("  " + " | ".join(f"{col:<15}" for col in columns))
        print("  " + "-" * (16 * len(columns) + len(columns) - 1))
        
        # Print each record
        for i, record in enumerate(records, 1):
            values = []
            for val in record:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, dict):
                    values.append(json.dumps(val)[:50] + "..." if len(json.dumps(val)) > 50 else json.dumps(val))
                else:
                    str_val = str(val)
                    values.append(str_val[:50] + "..." if len(str_val) > 50 else str_val)
            
            print(f"  " + " | ".join(f"{val:<15}" for val in values))
            
            # Limit output for large tables
            if i >= 10:
                print(f"  ... ({len(records) - 10} more records)")
                break
        
        print()

    conn.close()

if __name__ == "__main__":
    check_all_records() 