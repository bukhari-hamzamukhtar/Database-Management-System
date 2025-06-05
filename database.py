import psycopg2
from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Section {section} not found in {filename}")

    return db

def get_connection():
    try:
        params = config()
        conn = psycopg2.connect(**params)
        print("Connected to the database")
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None
