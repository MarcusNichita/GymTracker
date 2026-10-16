import customtkinter as ctk
import sqlite3
import bcrypt
from settings import DB_PATH
from workout import open_new_workout, open_past_workouts
from management import open_exercises_window, open_equipment_window, open_muscle_groups_window

# --- GUI Setup ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Gym Tracker - Login")
app.geometry("500x750")

# --- Dashboard Function ---
def open_dashboard(user_id):
    app.withdraw()

    dashboard = ctk.CTkToplevel()
    dashboard.title("Gym Tracker - Dashboard")
    dashboard.geometry("500x750")
    dashboard.protocol("WM_DELETE_WINDOW", app.destroy)

    label_welcome = ctk.CTkLabel(dashboard, text="Gym Tracker", font=("Times New Roman", 28, "bold"))
    label_welcome.pack(pady=(40, 20))

    btn_new_workout = ctk.CTkButton(dashboard, text="Log a Workout", height=50, width=250, font=("Times New Roman", 16, "bold"), command=lambda: open_new_workout(user_id, dashboard), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
    btn_new_workout.pack(pady=10)

    btn_exercises = ctk.CTkButton(dashboard, text="Exercises", height=50, width=250, font=("Times New Roman", 16, "bold"), command=lambda: open_exercises_window(user_id, dashboard), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
    btn_exercises.pack(pady=10)

    btn_equip = ctk.CTkButton(dashboard, text="Equipment", height=50, width=250, font=("Times New Roman", 16, "bold"), command=lambda: open_equipment_window(user_id, dashboard), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
    btn_equip.pack(pady=10)

    btn_muscle_groups = ctk.CTkButton(dashboard, text="Muscle Groups", height=50, width=250, font=("Times New Roman", 16, "bold"), command=lambda: open_muscle_groups_window(user_id, dashboard), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
    btn_muscle_groups.pack(pady=10)

    btn_history = ctk.CTkButton(dashboard, text="Workout History", height=50, width=250, font=("Times New Roman", 16, "bold"), command=lambda: open_past_workouts(user_id, dashboard), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
    btn_history.pack(pady=10)

    def logout():
        dashboard.destroy()
        entry_password.delete(0, 'end')
        lbl_status.configure(text="")
        app.deiconify()

    btn_logout = ctk.CTkButton(dashboard, text="Back to Login", command=logout, width=250, height=35, fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"), font=("Times New Roman", 14, "bold"))
    btn_logout.pack(pady=(20, 10))

    btn_exit_dash = ctk.CTkButton(dashboard, text="Exit Application", command=app.destroy, width=250, height=35, fg_color="#FFB7B2", hover_color="#E29C97", text_color="black", font=("Times New Roman", 14, "bold"))
    btn_exit_dash.pack(pady=10)

# --- Database & Logic Functions ---
def register_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        lbl_status.configure(text="Username or Password missing", text_color="#FF6B6B")
        return

    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)", (username, hashed_password.decode('utf-8')))
        conn.commit()

        lbl_status.configure(text="Account created! You can now log in.", text_color="green")
        entry_password.delete(0, 'end')
    except sqlite3.IntegrityError:
        lbl_status.configure(text="Username taken", text_color="#FF6B6B")
    finally:
        if conn: conn.close()

def login_user():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        lbl_status.configure(text="Username or Password missing", text_color="#FF6B6B")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.execute("SELECT id, password_hash FROM Users WHERE username = ?", (username,))
        result = cursor.fetchone()

        if result and bcrypt.checkpw(password.encode('utf-8'), result[1].encode('utf-8')):
            lbl_status.configure(text="")
            open_dashboard(result[0])
        else:
            lbl_status.configure(text="Username or Password invalid", text_color="#FF6B6B")
    except sqlite3.Error:
        lbl_status.configure(text="Database Error", text_color="#FF6B6B")
    finally:
        if conn: conn.close()

# --- Visual Elements (Login Screen) ---
label_title = ctk.CTkLabel(app, text="Gym Tracker", font=("Times New Roman", 28, "bold"))
label_title.pack(pady=(50, 10))

ctk.CTkLabel(app, text="Username:", font=("Times New Roman", 12)).pack(pady=(10, 0))
entry_username = ctk.CTkEntry(app, width=250, font=("Times New Roman", 12))
entry_username.pack(pady=(0, 10))

ctk.CTkLabel(app, text="Password:", font=("Times New Roman", 12)).pack(pady=(5, 0))
entry_password = ctk.CTkEntry(app, show="*", width=250, font=("Times New Roman", 12))
entry_password.pack(pady=(0, 10))

lbl_status = ctk.CTkLabel(app, text="", font=("Times New Roman", 12))
lbl_status.pack(pady=(0, 5))

btn_login = ctk.CTkButton(app, text="Login", command=login_user, width=250, height=35, font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black")
btn_login.pack(pady=(10, 10))

btn_register = ctk.CTkButton(app, text="Register", command=register_user, width=250, height=35, fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"), font=("Times New Roman", 14, "bold"))
btn_register.pack(pady=10)

btn_exit = ctk.CTkButton(app, text="Exit Application", command=app.destroy, width=250, height=35, fg_color="#FFB7B2", hover_color="#E29C97", text_color="black", font=("Times New Roman", 14, "bold"))
btn_exit.pack(pady=10)

if __name__ == "__main__":
    app.mainloop()