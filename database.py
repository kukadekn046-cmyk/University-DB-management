import pymysql
import pymysql.cursors
from config import Config

def get_db_connection(use_database=True):
    """
    Establishes and returns a PyMySQL connection with DictCursor.
    Handles charset and timezone consistently.
    """
    db_name = Config.DB_NAME if use_database else None
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=db_name,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        charset='utf8mb4'
    )

def execute_query(query, params=None, fetch=None, commit=False):
    """
    Executes a parameterized SQL query safely.
    
    :param query: SQL query string with %s placeholders
    :param params: tuple, list, or dict of parameters
    :param fetch: 'all', 'one', 'value', or None
    :param commit: True to commit changes (INSERT, UPDATE, DELETE)
    :return: List of dicts, single dict, single value, or cursor.lastrowid / rowcount
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params or ())
            
            result = None
            if fetch == 'all':
                result = cursor.fetchall()
            elif fetch == 'one':
                result = cursor.fetchone()
            elif fetch == 'value':
                row = cursor.fetchone()
                result = list(row.values())[0] if row else None
            elif commit:
                result = cursor.lastrowid or cursor.rowcount
            
            if commit:
                conn.commit()
            return result
    except Exception as e:
        if commit:
            conn.rollback()
        raise e
    finally:
        conn.close()

def init_db(schema_file='schema.sql'):
    """
    Initializes the database by creating it if it doesn't exist,
    and running schema.sql if tables are not yet present.
    """
    try:
        # First ensure database exists
        conn = get_db_connection(use_database=False)
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}`;")
        conn.commit()
        conn.close()

        # Check if tables exist
        conn = get_db_connection(use_database=True)
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            if not tables:
                print(f"[Database] No tables found in '{Config.DB_NAME}'. Executing {schema_file}...")
                with open(schema_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Strip single-line comments and execute statement-by-statement
                clean_lines = []
                for line in content.splitlines():
                    stripped = line.strip()
                    if not stripped.startswith('--'):
                        clean_lines.append(line)
                
                clean_sql = '\n'.join(clean_lines)
                for stmt in clean_sql.split(';'):
                    stmt = stmt.strip()
                    if stmt:
                        cursor.execute(stmt)
                conn.commit()
                print(f"[Database] Successfully initialized database schema from {schema_file}.")
            else:
                print(f"[Database] Found {len(tables)} existing tables in '{Config.DB_NAME}'. Database ready.")
        conn.close()
    except Exception as err:
        print(f"[Database Initialization Warning]: {err}")
