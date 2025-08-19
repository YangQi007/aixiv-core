import os
import psycopg2

def check_schema():
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    # Get all tables
    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
    tables = [row[0] for row in cur.fetchall()]

    print('Database Schema:')
    print('=' * 50)

    for table in sorted(tables):
        print(f'\nTable: {table}')
        print('-' * 30)
        
        # Get column information
        cur.execute("""
            SELECT 
                column_name, 
                data_type, 
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_name = %s 
            ORDER BY ordinal_position
        """, (table,))
        
        columns = cur.fetchall()
        for col in columns:
            name, dtype, max_len, nullable, default = col
            length_str = f'({max_len})' if max_len else ''
            nullable_str = 'NULL' if nullable == 'YES' else 'NOT NULL'
            default_str = f' DEFAULT {default}' if default else ''
            print(f'  {name}: {dtype}{length_str} {nullable_str}{default_str}')

    conn.close()

if __name__ == "__main__":
    check_schema() 