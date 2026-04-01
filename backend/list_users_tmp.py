
import sqlite3

def list_users():
    conn = sqlite3.connect('d:/jinglin/go/K-C-go/backend/community.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, role FROM users")
    rows = cursor.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Username: {row[1]}, Role: {row[3]}")
    conn.close()

if __name__ == "__main__":
    list_users()
