import socket
import tkinter as tk
from tkinter import messagebox, filedialog
import os
HOST = '127.0.0.1'
PORT = 5001
def get_submissions():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto("GET_SUBMISSIONS".encode('utf-8'), (HOST, PORT))
        submissions, _ = client_socket.recvfrom(1024*1024)
        submissions = submissions.decode('utf-8')

        client_socket.close()
        submissions_text.delete(1.0, tk.END)
        submissions_text.insert(tk.END, submissions)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
def open_file(filename):
    try:
        file_path = os.path.join("C:\\Users\\wasim\\Downloads\\informatics_gui\\uploads", filename)
        with open(file_path, 'r') as file:
            content = file.read()
        messagebox.showinfo("File Content", content)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while opening the file: {e}")
def add_points(username, points):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"ADD_POINTS {username} {points}".encode('utf-8'), (HOST, PORT))
        response, _ = client_socket.recvfrom(1024)
        response = response.decode('utf-8')

        client_socket.close()

        messagebox.showinfo("Success", response)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
def remove_points(username, points):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(f"REMOVE_POINTS {username} {points}".encode('utf-8'), (HOST, PORT))
        response, _ = client_socket.recvfrom(1024)
        response = response.decode('utf-8')

        client_socket.close()

        messagebox.showinfo("Success", response)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
def create_admin_dashboard():
    window = tk.Tk()
    window.title("Admin Dashboard")
    submissions_frame = tk.LabelFrame(window, text="Submissions", padx=10, pady=10)
    submissions_frame.pack(padx=20, pady=20)

    submissions_text = tk.Text(submissions_frame, height=10, width=50)
    submissions_text.pack()
    refresh_button = tk.Button(window, text="Refresh Submissions", command=get_submissions)
    refresh_button.pack(pady=10)
    points_frame = tk.LabelFrame(window, text="Modify Points", padx=10, pady=10)
    points_frame.pack(padx=20, pady=20)

    tk.Label(points_frame, text="Username:").grid(row=0, column=0)
    username_entry = tk.Entry(points_frame)
    username_entry.grid(row=0, column=1)

    tk.Label(points_frame, text="Points:").grid(row=1, column=0)
    points_entry = tk.Entry(points_frame)
    points_entry.grid(row=1, column=1)

    add_button = tk.Button(points_frame, text="Add Points", command=lambda: add_points(username_entry.get(), points_entry.get()))
    add_button.grid(row=2, column=0, pady=10)

    remove_button = tk.Button(points_frame, text="Remove Points", command=lambda: remove_points(username_entry.get(), points_entry.get()))
    remove_button.grid(row=2, column=1, pady=10)

    window.mainloop()

if __name__ == "__main__":
    create_admin_dashboard()
