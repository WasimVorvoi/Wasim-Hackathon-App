import socket
import sqlite3
import os
import datetime

DB_FILE = r"C:\Users\wasim\Downloads\informatics_gui\database.db"
HOST = '127.0.0.1'
PORT = 5001
UPLOAD_DIR = r"C:\Users\wasim\Downloads\informatics_gui\uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            score INTEGER DEFAULT 0,
            role TEXT DEFAULT 'student'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            filename TEXT,
            file_path TEXT
        )
    ''')
    conn.commit()
    conn.close()
def log(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")
def handle_client(data, addr, server_socket):
    try:
        request = data.decode('utf-8')
        response = ""
        if request.startswith("REGISTER"):
            _, username, password = request.split(" ")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                response = "Registration successful."
            except sqlite3.IntegrityError:
                response = "Username already exists."
            conn.close()

        elif request.startswith("LOGIN"):
            _, username, password = request.split(" ")
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
            result = c.fetchone()
            conn.close()
            if result:
                response = f"Login successful. Role: {result[0]}"
            else:
                response = "Invalid username or password."

        elif request.startswith("UPLOAD_FILE"):
            _, username, filename = request.split(" ", 1)
            file_data, _ = server_socket.recvfrom(1024*1024)
            file_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(file_data)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO submissions (username, filename, file_path) VALUES (?, ?, ?)", 
                      (username, filename, file_path))
            conn.commit()
            conn.close()

            log(f"File uploaded: {filename} by user: {addr}")
            server_socket.sendto(b"File uploaded successfully!", addr)
            notify_admin(f"New file submitted by {username}: {filename}")

        elif request.startswith("GET_SUBMISSIONS"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT filename FROM submissions ORDER BY id DESC")
            submissions = c.fetchall()
            conn.close()
            submissions_str = "\n".join([f"User has submitted: {row[0]}" for row in submissions])
            server_socket.sendto(submissions_str.encode('utf-8'), addr)

        elif request.startswith("GET_LEADERBOARD"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username, score FROM users ORDER BY score DESC")
            leaderboard = c.fetchall()
            conn.close()
            leaderboard_str = "\n".join([f"{row[0]}: {row[1]} points" for row in leaderboard])
            server_socket.sendto(leaderboard_str.encode('utf-8'), addr)

        elif request.startswith("ADD_POINTS"):
            _, username, points = request.split(" ")
            points = int(points)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE users SET score = score + ? WHERE username = ?", (points, username))
            conn.commit()
            conn.close()
            response = f"Added {points} points to {username}"

        elif request.startswith("REMOVE_POINTS"):
            _, username, points = request.split(" ")
            points = int(points)
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE users SET score = score - ? WHERE username = ?", (points, username))
            conn.commit()
            conn.close()
            response = f"Removed {points} points from {username}"

        else:
            response = "Invalid command."
        server_socket.sendto(response.encode('utf-8'), addr)

    except Exception as e:
        log(f"Error: {e}")
        server_socket.sendto(b"Error processing request.", addr)
def notify_admin(message):
    print(f"Admin Notification: {message}")
def start_server():
    init_db()
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    log(f"UDP Server started on {HOST}:{PORT}")
    while True:
        try:
            data, addr = server_socket.recvfrom(1024*1024)
            handle_client(data, addr, server_socket)
        except Exception as e:
            log(f"Error receiving data: {e}")
            break
if __name__ == "__main__":
    start_server()
