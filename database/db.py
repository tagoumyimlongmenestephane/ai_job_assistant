import psycopg

def get_connection():
    connection = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="job_assistant",
        user="postgres",
        password="job_assistant_password"
    )
     
    return connection

if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Connection to the database was successful.")
        conn.close()