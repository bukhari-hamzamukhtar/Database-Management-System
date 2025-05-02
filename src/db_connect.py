try:
    import psycopg2
except ImportError:
    raise ImportError("psycopg2 module is not installed.")

conn = psycopg2.connect(
    dbname="Music Player",
    user="postgres",
    password="enter_password",
    host="localhost",
    port="5432"
)
print("Connected to database!")
conn.close()