import psycopg2

try:
    conn = psycopg2.connect(
        host='192.168.2.59',
        database='tradifyerp_db', 
        user='tradifyerp_user',
        password='Tradify@PostgreSQL2024',
        port='5432'
    )
    print('PostgreSQL connection successful')
    cursor = conn.cursor()
    cursor.execute('SELECT current_database()')
    result = cursor.fetchone()
    print('Connected to database:', result[0])
    cursor.close()
    conn.close()
except Exception as e:
    print('PostgreSQL connection failed:', str(e))