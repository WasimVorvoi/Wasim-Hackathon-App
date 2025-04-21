import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import os

HOST = '127.0.0.1'
PORT = 5001
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

UPLOAD_DIR = r"C:\Users\wasim\Downloads\informatics_gui\uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
def send_request(request):
    CLIENT_SOCKET.sendto(request.encode('utf-8'), (HOST, PORT))
    response, _ = CLIENT_SOCKET.recvfrom(1024*1024)
    return response.decode('utf-8')
def register_user(username, password):
    request = f"REGISTER {username} {password}"
    response = send_request(request)
    return response
def login_user(username, password):
    request = f"LOGIN {username} {password}"
    response = send_request(request)
    return response
def upload_file(username, filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'rb') as f:
        file_data = f.read()
    request = f"UPLOAD_FILE {username} {filename}"
    send_request(request)
    CLIENT_SOCKET.sendto(file_data, (HOST, PORT))

    response = CLIENT_SOCKET.recvfrom(1024*1024)[0].decode('utf-8')
    return response
def view_leaderboard():
    request = "GET_LEADERBOARD"
    response = send_request(request)
    return response
def view_questions():
    request = "GET_QUESTIONS"
    response = send_request(request)
    return response
def show_login_register_window():
    def handle_register():
        username = entry_username.get()
        password = entry_password.get()
        if not username or not password:
            messagebox.showerror("Error", "Both fields are required.")
            return

        response = register_user(username, password)
        messagebox.showinfo("Info", response)
        if "Registration successful" in response:
            show_main_menu(username)

    def handle_login():
        username = entry_username.get()
        password = entry_password.get()
        if not username or not password:
            messagebox.showerror("Error", "Both fields are required.")
            return

        response = login_user(username, password)
        messagebox.showinfo("Info", response)
        if "Login successful" in response:
            show_main_menu(username)

    login_window = tk.Tk()
    login_window.title("Login/Register")
    label_username = tk.Label(login_window, text="Username")
    label_username.pack(pady=5)
    entry_username = tk.Entry(login_window)
    entry_username.pack(pady=5)
    label_password = tk.Label(login_window, text="Password")
    label_password.pack(pady=5)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.pack(pady=5)
    button_register = tk.Button(login_window, text="Register", command=handle_register)
    button_register.pack(pady=5)
    button_login = tk.Button(login_window, text="Login", command=handle_login)
    button_login.pack(pady=5)

    login_window.mainloop()
def show_main_menu(username):
    def handle_upload_file():
        filepath = filedialog.askopenfilename(title="Select a File", filetypes=[("Text Files", "*.txt")])
        if filepath:
            response = upload_file(username, filepath)
            messagebox.showinfo("Info", response)

    def handle_refresh_questions():
        questions = view_questions()
        question_listbox.delete(0, tk.END)
        questions = questions.split('\n')
        for question in questions:
            question_listbox.insert(tk.END, question)

    def handle_refresh_leaderboard():
        leaderboard = view_leaderboard()
        leaderboard_listbox.delete(0, tk.END)
        leaderboard = leaderboard.split('\n')
        for entry in leaderboard:
            leaderboard_listbox.insert(tk.END, entry)

    main_menu_window = tk.Tk()
    main_menu_window.title("Main Menu")
    notebook = ttk.Notebook(main_menu_window)
    notebook.pack(fill='both', expand=True)
    questions_frame = ttk.Frame(notebook)
    leaderboard_frame = ttk.Frame(notebook)
    notebook.add(questions_frame, text='Questions')
    notebook.add(leaderboard_frame, text='Leaderboard')
    question_label = tk.Label(questions_frame, text="Questions", font=("Arial", 14))
    question_label.pack(pady=10)
    question_listbox = tk.Listbox(questions_frame, width=50, height=15)
    question_listbox.pack(pady=10)
    refresh_questions_button = tk.Button(questions_frame, text="Refresh", command=handle_refresh_questions)
    refresh_questions_button.pack(pady=10)
    upload_button = tk.Button(questions_frame, text="Upload File", command=handle_upload_file)
    upload_button.pack(pady=10)
    leaderboard_label = tk.Label(leaderboard_frame, text="Leaderboard", font=("Arial", 14))
    leaderboard_label.pack(pady=10)
    leaderboard_listbox = tk.Listbox(leaderboard_frame, width=50, height=15)
    leaderboard_listbox.pack(pady=10)
    refresh_leaderboard_button = tk.Button(leaderboard_frame, text="Refresh", command=handle_refresh_leaderboard)
    refresh_leaderboard_button.pack(pady=10)
    label_welcome = tk.Label(main_menu_window, text=f"Welcome, {username}!", font=("Arial", 14))
    label_welcome.pack(pady=20)
    button_logout = tk.Button(main_menu_window, text="Logout", command=main_menu_window.quit)
    button_logout.pack(pady=10)
    handle_refresh_questions()
    handle_refresh_leaderboard()

    main_menu_window.mainloop()
if __name__ == "__main__":
    show_login_register_window()
