import customtkinter as ctk
import tkinter as tk
import sqlite3
import bcrypt
import datetime
import os
import sys


# --- Path Helper for EXE ---
def resource_path(relative_path):
    """ Get path to resource, works for dev and for when running as EXE """
    if getattr(sys, 'frozen', False):
        # If running as EXE (compiled), look in the folder where the EXE is located
        base_path = os.path.dirname(sys.executable)
    else:
        # If running as script (in IDE), look in the current project folder
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


DB_PATH = resource_path('gym_tracker.db')

# --- GUI Setup ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Gym Tracker - Login")
app.geometry("500x750")


# --- New Workout Function ---
def open_new_workout(user_id, parent_window):
    parent_window.withdraw()

    workout_window = ctk.CTkToplevel()
    workout_window.title("New Workout")
    workout_window.geometry("500x750")

    current_set = ctk.IntVar(value=1)

    def close_and_go_back():
        workout_window.destroy()
        parent_window.deiconify()

    workout_window.protocol("WM_DELETE_WINDOW", close_and_go_back)

    # Title
    ctk.CTkLabel(workout_window, text="Log a Workout", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    # Date Section
    ctk.CTkLabel(workout_window, text="Date (DD/MM/YYYY):", font=("Times New Roman", 12)).pack(pady=(5, 0))
    entry_date = ctk.CTkEntry(workout_window, width=250, font=("Times New Roman", 12))
    entry_date.pack()
    entry_date.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

    lbl_error_date = ctk.CTkLabel(workout_window, text="", font=("Times New Roman", 12), text_color="#FF6B6B")
    lbl_error_date.pack(pady=(0, 5))

    # --- DATABASE DATA FETCHING ---
    def get_muscle_groups():
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM MuscleGroups ORDER BY name ASC")
            results = [row[0] for row in cursor.fetchall()]
            return results if results else ["(No data)"]
        except sqlite3.Error:
            return ["(Database Error)"]
        finally:
            if conn:
                conn.close()

    def get_equipment():
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM Equipment ORDER BY name ASC")
            results = [row[0] for row in cursor.fetchall()]
            return results if results else ["(No data)"]
        except sqlite3.Error:
            return ["(Database Error)"]
        finally:
            if conn:
                conn.close()

    def on_muscle_change(selected_muscle):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT e.exercise_name
                           FROM Exercises e
                                    JOIN MuscleGroups m ON e.muscle_group_id = m.id
                           WHERE m.name = ?
                           ORDER BY e.exercise_name ASC
                           ''', (selected_muscle,))
            results = [row[0] for row in cursor.fetchall()]

            combo_exercise.configure(values=results if results else ["(No exercises found)"])
            combo_exercise.set("")
        except sqlite3.Error:
            combo_exercise.configure(values=["(Error)"])
        finally:
            if conn:
                conn.close()

    # Muscle Group Section
    ctk.CTkLabel(workout_window, text="Muscle Group Worked:", font=("Times New Roman", 12)).pack(pady=(5, 0))
    muscle_groups = get_muscle_groups()
    combo_muscle = ctk.CTkOptionMenu(workout_window, values=muscle_groups, command=on_muscle_change, width=250,
                                     fg_color="#A8E6CF", button_color="#88D4AB", button_hover_color="#7AC29A",
                                     text_color="black")
    combo_muscle.set("")
    combo_muscle.pack()

    # Dynamic UI logic for Equipment Type (Simplified - weight is always visible now)
    def on_equipment_change(choice):
        pass  # Everything uses the same 3-box input now

    # Equipment Type Section
    ctk.CTkLabel(workout_window, text="Equipment Used:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    equipment_types = get_equipment()
    combo_equipment = ctk.CTkOptionMenu(workout_window, values=equipment_types, command=on_equipment_change, width=250,
                                        fg_color="#A8E6CF", button_color="#88D4AB", button_hover_color="#7AC29A",
                                        text_color="black")
    combo_equipment.set("")
    combo_equipment.pack()

    # Dynamic UI logic for changing exercises
    def on_exercise_change(choice):
        current_set.set(1)
        lbl_current_set.configure(text="Recording a set")

    # Exercise Name
    ctk.CTkLabel(workout_window, text="Exercise:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    combo_exercise = ctk.CTkOptionMenu(workout_window, values=["(Select muscle group first)"], width=250,
                                       command=on_exercise_change, fg_color="#A8E6CF", button_color="#88D4AB",
                                       button_hover_color="#7AC29A", text_color="black")
    combo_exercise.set("")
    combo_exercise.pack()

    # Inline Error label for Dropdowns
    lbl_error_dropdowns = ctk.CTkLabel(workout_window, text="", font=("Times New Roman", 12), text_color="#FF6B6B")
    lbl_error_dropdowns.pack(pady=(5, 0))

    # Divider Line
    ctk.CTkFrame(workout_window, height=2, width=400, fg_color="gray").pack(pady=10)

    # Current Set Tracker
    lbl_current_set = ctk.CTkLabel(workout_window, text="Recording a set", font=("Times New Roman", 18, "bold"),
                                   text_color="#88D4AB")
    lbl_current_set.pack(pady=(0, 10))

    # Universal Stats Section (Sets, Reps, Weight)
    frame_stats = ctk.CTkFrame(workout_window, fg_color="transparent")
    frame_stats.pack(pady=5)

    label_sets = ctk.CTkLabel(frame_stats, text="Sets (Opt):", font=("Times New Roman", 12))
    label_sets.grid(row=0, column=0, padx=(0, 5), sticky="w")
    entry_sets = ctk.CTkEntry(frame_stats, width=80, font=("Times New Roman", 12))
    entry_sets.grid(row=1, column=0, padx=(0, 5))

    label_reps = ctk.CTkLabel(frame_stats, text="Reps:", font=("Times New Roman", 12))
    label_reps.grid(row=0, column=1, padx=(5, 5), sticky="w")
    entry_reps = ctk.CTkEntry(frame_stats, width=80, font=("Times New Roman", 12))
    entry_reps.grid(row=1, column=1, padx=(5, 5))

    label_weight = ctk.CTkLabel(frame_stats, text="Weight (kg):", font=("Times New Roman", 12))
    label_weight.grid(row=0, column=2, padx=(5, 0), sticky="w")
    entry_weight = ctk.CTkEntry(frame_stats, width=80, font=("Times New Roman", 12))
    entry_weight.grid(row=1, column=2, padx=(5, 0))

    # Inline Error label for Stats
    lbl_error_stats = ctk.CTkLabel(workout_window, text="", font=("Times New Roman", 12), text_color="#FF6B6B")
    lbl_error_stats.pack(pady=(0, 5))

    def add_set():
        lbl_error_date.configure(text="")
        lbl_error_dropdowns.configure(text="")
        lbl_error_stats.configure(text="")

        raw_date_str = entry_date.get().strip()
        muscle = combo_muscle.get()
        equip = combo_equipment.get()
        ex_name = combo_exercise.get()

        sets_str = entry_sets.get().strip()
        reps_str = entry_reps.get().strip()
        weight_str = entry_weight.get().strip()
        set_num = current_set.get()

        has_error = False
        date_str = ""

        # --- Date Validation ---
        if not raw_date_str:
            lbl_error_date.configure(text="Date missing")
            has_error = True
        else:
            try:
                parsed_date = datetime.datetime.strptime(raw_date_str, "%d/%m/%Y").date()
                if parsed_date > datetime.date.today():
                    lbl_error_date.configure(text="Date invalid")
                    has_error = True
                else:
                    date_str = parsed_date.strftime("%d/%m/%Y")
            except ValueError:
                lbl_error_date.configure(text="Date invalid")
                has_error = True

        # --- Dropdown Validation ---
        invalid_selections = ["", "(No data)", "(Database Error)", "(Select muscle group first)",
                              "(No exercises found)", "(Error)"]
        if muscle in invalid_selections or ex_name in invalid_selections or equip in invalid_selections:
            lbl_error_dropdowns.configure(text="Dropdown selection missing")
            has_error = True

        # --- Stats Validation (Sets, Reps, Weight) ---
        sets_count = 1
        reps_val = 0
        weight_val = 0.0

        if not has_error:
            if sets_str:
                try:
                    sets_count = int(sets_str)
                    if sets_count <= 0: raise ValueError
                except ValueError:
                    lbl_error_stats.configure(text="Sets must be a positive integer.")
                    has_error = True

            if not has_error:
                if not reps_str:
                    lbl_error_stats.configure(text="Reps cannot be empty.")
                    has_error = True
                else:
                    try:
                        reps_val = float(reps_str)
                        if reps_val <= 0: raise ValueError
                    except ValueError:
                        lbl_error_stats.configure(text="Reps must be a positive number.")
                        has_error = True

            if not has_error:
                if weight_str:
                    try:
                        weight_val = float(weight_str)
                        if weight_val < 0: raise ValueError
                    except ValueError:
                        lbl_error_stats.configure(text="Weight must be a valid number.")
                        has_error = True

        if has_error:
            return

        # ---------------- DATABASE SAVING LOGIC ----------------
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM MuscleGroups WHERE name = ?", (muscle,))
            muscle_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM Exercises WHERE exercise_name = ?", (ex_name,))
            exercise_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM Equipment WHERE name = ?", (equip,))
            equipment_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM Workouts WHERE user_id = ? AND date = ? AND muscle_group_id = ?",
                           (user_id, date_str, muscle_id))
            workout_row = cursor.fetchone()

            if workout_row:
                workout_id = workout_row[0]
            else:
                cursor.execute("INSERT INTO Workouts (user_id, date, muscle_group_id) VALUES (?, ?, ?)",
                               (user_id, date_str, muscle_id))
                workout_id = cursor.lastrowid

            # Loop and insert based on how many sets the user specified
            for _ in range(sets_count):
                cursor.execute('''INSERT INTO WorkoutSets (workout_id, exercise_id, equipment_id, weight_kg, reps)
                                  VALUES (?, ?, ?, ?, ?)''',
                               (workout_id, exercise_id, equipment_id, weight_val, reps_val))
            conn.commit()

        except sqlite3.Error as e:
            lbl_error_stats.configure(text=f"DB Error: {e}")
            return
        finally:
            if conn:
                conn.close()

        current_set.set(set_num + sets_count)

        entry_sets.delete(0, 'end')
        entry_reps.delete(0, 'end')
        entry_weight.delete(0, 'end')
        entry_sets.focus()

    btn_add_set = ctk.CTkButton(workout_window, text="Add Set(s)", command=add_set, width=250, height=35,
                                font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                                text_color="black")
    btn_add_set.pack(pady=(10, 15))

    btn_back = ctk.CTkButton(workout_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                             fg_color="transparent", border_width=2, border_color="#A8E6CF",
                             text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
    btn_back.pack(pady=(5, 10))


# --- Exercises Function ---
def open_exercises_window(user_id, parent_window):
    parent_window.withdraw()
    ex_window = ctk.CTkToplevel()
    ex_window.title("Exercises")
    ex_window.geometry("500x750")

    def close_and_go_back():
        ex_window.destroy()
        parent_window.deiconify()

    ex_window.protocol("WM_DELETE_WINDOW", close_and_go_back)

    ctk.CTkLabel(ex_window, text="Exercises", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    def update_exercise_list(muscle_name):
        listbox_exercises.delete(0, 'end')
        if not muscle_name or muscle_name in ["", "(No data)", "(Database Error)"]:
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute('''
                           SELECT e.exercise_name
                           FROM Exercises e
                                    JOIN MuscleGroups m ON e.muscle_group_id = m.id
                           WHERE m.name = ?
                           ORDER BY e.exercise_name ASC
                           ''', (muscle_name,))
            for row in cursor.fetchall():
                listbox_exercises.insert('end', row[0])
        except sqlite3.Error:
            listbox_exercises.insert('end', "Error loading exercises")
        finally:
            if conn:
                conn.close()

    def get_muscle_groups():
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM MuscleGroups ORDER BY name ASC")
            results = [row[0] for row in cursor.fetchall()]
            return results if results else ["(No data)"]
        except sqlite3.Error:
            return ["(Database Error)"]
        finally:
            if conn:
                conn.close()

    ctk.CTkLabel(ex_window, text="Target Muscle Group:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    muscle_groups = get_muscle_groups()
    combo_muscle = ctk.CTkOptionMenu(ex_window, values=muscle_groups, width=250, command=update_exercise_list,
                                     fg_color="#A8E6CF", button_color="#88D4AB", button_hover_color="#7AC29A",
                                     text_color="black")
    combo_muscle.set("")
    combo_muscle.pack()

    ctk.CTkLabel(ex_window, text="Add New Exercise:", font=("Times New Roman", 12)).pack(pady=(20, 0))
    entry_ex_name = ctk.CTkEntry(ex_window, width=250, font=("Times New Roman", 12))
    entry_ex_name.pack()

    lbl_status_ex = ctk.CTkLabel(ex_window, text="", font=("Times New Roman", 12))
    lbl_status_ex.pack(pady=(5, 5))

    def save_exercise():
        muscle_name = combo_muscle.get()
        ex_name = entry_ex_name.get().strip()

        invalid_selections = ["", "(No data)", "(Database Error)"]
        if muscle_name in invalid_selections:
            lbl_status_ex.configure(text="Muscle group missing.", text_color="#FF6B6B")
            return

        if not ex_name:
            lbl_status_ex.configure(text="Exercise name missing.", text_color="#FF6B6B")
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM MuscleGroups WHERE name = ?", (muscle_name,))
            result = cursor.fetchone()

            if not result:
                lbl_status_ex.configure(text="Error: Muscle group not found in DB.", text_color="#FF6B6B")
                return

            muscle_group_id = result[0]

            cursor.execute("INSERT INTO Exercises (exercise_name, muscle_group_id) VALUES (?, ?)",
                           (ex_name, muscle_group_id))
            conn.commit()

            lbl_status_ex.configure(text=f"'{ex_name}' added successfully!", text_color="green")
            entry_ex_name.delete(0, 'end')

            update_exercise_list(muscle_name)

        except sqlite3.IntegrityError:
            lbl_status_ex.configure(text="This exercise already exists.", text_color="#FF6B6B")
        except sqlite3.Error:
            lbl_status_ex.configure(text="A database error occurred.", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    btn_save = ctk.CTkButton(ex_window, text="Add Exercise", command=save_exercise, width=250, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_save.pack(pady=(0, 15))

    ctk.CTkFrame(ex_window, height=2, width=350, fg_color="gray").pack(pady=5)

    ctk.CTkLabel(ex_window, text="Exercises in Selected Group:", font=("Times New Roman", 12)).pack(pady=(5, 5))

    frame_list = ctk.CTkFrame(ex_window)
    frame_list.pack(pady=5, padx=40, fill="both", expand=True)

    listbox_exercises = tk.Listbox(frame_list, font=("Times New Roman", 14), bg="#2b2b2b", fg="white",
                                   selectbackground="#88D4AB", selectforeground="black", highlightthickness=0,
                                   borderwidth=0)
    listbox_exercises.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    scrollbar = ctk.CTkScrollbar(frame_list, command=listbox_exercises.yview)
    scrollbar.pack(side="right", fill="y", padx=5, pady=10)
    listbox_exercises.configure(yscrollcommand=scrollbar.set)

    def view_exercise_details():
        selection = listbox_exercises.curselection()
        if not selection:
            return

        ex_name = listbox_exercises.get(selection[0])

        ex_window.withdraw()
        details_window = ctk.CTkToplevel()
        details_window.title("Exercise Details")
        details_window.geometry("500x750")

        def close_details_and_go_back():
            details_window.destroy()
            ex_window.deiconify()

        details_window.protocol("WM_DELETE_WINDOW", close_details_and_go_back)

        ctk.CTkLabel(details_window, text=ex_name, font=("Times New Roman", 22, "bold"), text_color="#88D4AB").pack(
            pady=(30, 20))

        ctk.CTkLabel(details_window, text="Coming soon", font=("Times New Roman", 36, "bold")).pack(expand=True)

        ctk.CTkButton(details_window, text="Back to Exercises", command=close_details_and_go_back, width=250, height=35,
                      fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=30)

    def edit_selected_exercise():
        selection = listbox_exercises.curselection()
        if not selection:
            return

        old_name = listbox_exercises.get(selection[0])

        edit_win = ctk.CTkToplevel(ex_window)
        edit_win.title("Edit Exercise")
        edit_win.geometry("300x200")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text=f"Edit: {old_name}", font=("Times New Roman", 16, "bold")).pack(pady=(20, 10))
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=5)
        entry_edit.insert(0, old_name)

        def save_edit():
            new_name = entry_edit.get().strip()
            if not new_name or new_name == old_name:
                edit_win.destroy()
                return

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("UPDATE Exercises SET exercise_name = ? WHERE exercise_name = ?", (new_name, old_name))
                conn.commit()
                lbl_status_ex.configure(text=f"Renamed to '{new_name}'.", text_color="green")
                update_exercise_list(combo_muscle.get())
            except sqlite3.IntegrityError:
                lbl_status_ex.configure(text="Name already exists.", text_color="#FF6B6B")
            except sqlite3.Error:
                lbl_status_ex.configure(text="Database Error.", text_color="#FF6B6B")
            finally:
                if conn:
                    conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save", command=save_edit, fg_color="#A8E6CF", hover_color="#88D4AB",
                      text_color="black").pack(pady=15)

    def delete_selected_exercise():
        selection = listbox_exercises.curselection()
        if not selection:
            return

        ex_name_to_delete = listbox_exercises.get(selection[0])

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Exercises WHERE exercise_name = ?", (ex_name_to_delete,))
            ex_id_row = cursor.fetchone()
            if ex_id_row:
                ex_id = ex_id_row[0]
                cursor.execute("SELECT 1 FROM WorkoutSets WHERE exercise_id = ? LIMIT 1", (ex_id,))
                if cursor.fetchone():
                    lbl_status_ex.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return

            cursor.execute("DELETE FROM Exercises WHERE exercise_name = ?", (ex_name_to_delete,))
            conn.commit()

            lbl_status_ex.configure(text=f"'{ex_name_to_delete}' deleted.", text_color="green")
            update_exercise_list(combo_muscle.get())
        except sqlite3.Error as e:
            lbl_status_ex.configure(text=f"Error: {e}", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    frame_buttons = ctk.CTkFrame(ex_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))

    btn_view = ctk.CTkButton(frame_buttons, text="View Details", command=view_exercise_details, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_view.pack(side="left", padx=5)

    btn_edit = ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_exercise, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", hover_color="#E2BE93",
                             text_color="black")
    btn_edit.pack(side="left", padx=5)

    btn_delete = ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_exercise,
                               width=130, height=35, fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                               font=("Times New Roman", 14, "bold"))
    btn_delete.pack(side="left", padx=5)

    btn_back = ctk.CTkButton(ex_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                             fg_color="transparent", border_width=2, border_color="#A8E6CF",
                             text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
    btn_back.pack(side="bottom", pady=20)


# --- Equipment Function ---
def open_equipment_window(user_id, parent_window):
    parent_window.withdraw()
    equip_window = ctk.CTkToplevel()
    equip_window.title("Equipment")
    equip_window.geometry("500x750")

    def close_and_go_back():
        equip_window.destroy()
        parent_window.deiconify()

    equip_window.protocol("WM_DELETE_WINDOW", close_and_go_back)

    ctk.CTkLabel(equip_window, text="Equipment", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    ctk.CTkLabel(equip_window, text="Add New Equipment:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    entry_equip_name = ctk.CTkEntry(equip_window, width=250, font=("Times New Roman", 12))
    entry_equip_name.pack(pady=(0, 5))

    var_req_weight = ctk.IntVar(value=0)
    chk_req_weight = ctk.CTkCheckBox(equip_window, text="Requires Weight (kg)?", font=("Times New Roman", 12),
                                     variable=var_req_weight, fg_color="#A8E6CF", hover_color="#88D4AB")
    chk_req_weight.pack(pady=(5, 5))

    lbl_status_equip = ctk.CTkLabel(equip_window, text="", font=("Times New Roman", 12))
    lbl_status_equip.pack(pady=(5, 5))

    def update_equipment_list():
        listbox_equipment.delete(0, 'end')
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM Equipment ORDER BY name ASC")
            for row in cursor.fetchall():
                listbox_equipment.insert('end', row[0])
        except sqlite3.Error:
            listbox_equipment.insert('end', "Error loading equipment")
        finally:
            if conn:
                conn.close()

    def save_equipment():
        equip_name = entry_equip_name.get().strip()
        req_weight_val = var_req_weight.get()

        if not equip_name:
            lbl_status_equip.configure(text="Equipment name missing.", text_color="#FF6B6B")
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO Equipment (name, requires_weight) VALUES (?, ?)", (equip_name, req_weight_val))
            conn.commit()

            lbl_status_equip.configure(text=f"'{equip_name}' added successfully!", text_color="green")
            entry_equip_name.delete(0, 'end')
            var_req_weight.set(0)

            update_equipment_list()

        except sqlite3.IntegrityError:
            lbl_status_equip.configure(text="This equipment already exists.", text_color="#FF6B6B")
        except sqlite3.Error:
            lbl_status_equip.configure(text="A database error occurred.", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    btn_save = ctk.CTkButton(equip_window, text="Add Equipment", command=save_equipment, width=250, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_save.pack(pady=(0, 15))

    ctk.CTkFrame(equip_window, height=2, width=350, fg_color="gray").pack(pady=5)

    ctk.CTkLabel(equip_window, text="Current Equipment:", font=("Times New Roman", 12)).pack(pady=(5, 5))

    frame_list = ctk.CTkFrame(equip_window)
    frame_list.pack(pady=5, padx=40, fill="both", expand=True)

    listbox_equipment = tk.Listbox(frame_list, font=("Times New Roman", 14), bg="#2b2b2b", fg="white",
                                   selectbackground="#88D4AB", selectforeground="black", highlightthickness=0,
                                   borderwidth=0)
    listbox_equipment.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    scrollbar = ctk.CTkScrollbar(frame_list, command=listbox_equipment.yview)
    scrollbar.pack(side="right", fill="y", padx=5, pady=10)
    listbox_equipment.configure(yscrollcommand=scrollbar.set)

    update_equipment_list()

    def view_equipment_details():
        selection = listbox_equipment.curselection()
        if not selection:
            return

        equip_name = listbox_equipment.get(selection[0])

        equip_window.withdraw()
        details_window = ctk.CTkToplevel()
        details_window.title("Equipment Details")
        details_window.geometry("500x750")

        def close_details_and_go_back():
            details_window.destroy()
            equip_window.deiconify()

        details_window.protocol("WM_DELETE_WINDOW", close_details_and_go_back)

        ctk.CTkLabel(details_window, text=equip_name, font=("Times New Roman", 22, "bold"), text_color="#88D4AB").pack(
            pady=(30, 20))

        ctk.CTkLabel(details_window, text="Coming soon", font=("Times New Roman", 36, "bold")).pack(expand=True)

        ctk.CTkButton(details_window, text="Back to Equipment", command=close_details_and_go_back, width=250, height=35,
                      fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=30)

    def edit_selected_equipment():
        selection = listbox_equipment.curselection()
        if not selection:
            return

        old_name = listbox_equipment.get(selection[0])

        conn = None
        old_req_weight = 0
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT requires_weight FROM Equipment WHERE name = ?", (old_name,))
            row = cursor.fetchone()
            if row:
                old_req_weight = row[0]
        except sqlite3.Error:
            pass
        finally:
            if conn:
                conn.close()

        edit_win = ctk.CTkToplevel(equip_window)
        edit_win.title("Edit Equipment")
        edit_win.geometry("300x250")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text=f"Edit: {old_name}", font=("Times New Roman", 16, "bold")).pack(pady=(20, 10))
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=5)
        entry_edit.insert(0, old_name)

        var_edit_req = ctk.IntVar(value=old_req_weight)
        chk_edit_req = ctk.CTkCheckBox(edit_win, text="Requires Weight (kg)?", variable=var_edit_req,
                                       fg_color="#A8E6CF", hover_color="#88D4AB")
        chk_edit_req.pack(pady=10)

        def save_edit():
            new_name = entry_edit.get().strip()
            new_req = var_edit_req.get()
            if not new_name:
                return

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("UPDATE Equipment SET name = ?, requires_weight = ? WHERE name = ?",
                               (new_name, new_req, old_name))
                conn.commit()
                lbl_status_equip.configure(text=f"Updated '{new_name}'.", text_color="green")
                update_equipment_list()
            except sqlite3.IntegrityError:
                lbl_status_equip.configure(text="Name already exists.", text_color="#FF6B6B")
            except sqlite3.Error:
                lbl_status_equip.configure(text="Database Error.", text_color="#FF6B6B")
            finally:
                if conn:
                    conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save Changes", command=save_edit, fg_color="#A8E6CF", hover_color="#88D4AB",
                      text_color="black").pack(pady=15)

    def delete_selected_equipment():
        selection = listbox_equipment.curselection()
        if not selection:
            return

        equip_to_delete = listbox_equipment.get(selection[0])

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Equipment WHERE name = ?", (equip_to_delete,))
            eq_id_row = cursor.fetchone()
            if eq_id_row:
                eq_id = eq_id_row[0]
                cursor.execute("SELECT 1 FROM WorkoutSets WHERE equipment_id = ? LIMIT 1", (eq_id,))
                if cursor.fetchone():
                    lbl_status_equip.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return

            cursor.execute("DELETE FROM Equipment WHERE name = ?", (equip_to_delete,))
            conn.commit()

            lbl_status_equip.configure(text=f"'{equip_to_delete}' deleted.", text_color="green")
            update_equipment_list()
        except sqlite3.Error as e:
            lbl_status_equip.configure(text=f"Error: {e}", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    frame_buttons = ctk.CTkFrame(equip_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))

    btn_view = ctk.CTkButton(frame_buttons, text="View Details", command=view_equipment_details, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_view.pack(side="left", padx=5)

    btn_edit = ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_equipment, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", hover_color="#E2BE93",
                             text_color="black")
    btn_edit.pack(side="left", padx=5)

    btn_delete = ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_equipment,
                               width=130, height=35, fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                               font=("Times New Roman", 14, "bold"))
    btn_delete.pack(side="left", padx=5)

    btn_back = ctk.CTkButton(equip_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                             fg_color="transparent", border_width=2, border_color="#A8E6CF",
                             text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
    btn_back.pack(side="bottom", pady=20)


# --- Muscle Groups Function ---
def open_muscle_groups_window(user_id, parent_window):
    parent_window.withdraw()
    muscle_window = ctk.CTkToplevel()
    muscle_window.title("Muscle Groups")
    muscle_window.geometry("500x750")

    def close_and_go_back():
        muscle_window.destroy()
        parent_window.deiconify()

    muscle_window.protocol("WM_DELETE_WINDOW", close_and_go_back)

    ctk.CTkLabel(muscle_window, text="Muscle Groups", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    ctk.CTkLabel(muscle_window, text="Add New Muscle Group:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    entry_muscle_name = ctk.CTkEntry(muscle_window, width=250, font=("Times New Roman", 12))
    entry_muscle_name.pack()

    lbl_status_muscle = ctk.CTkLabel(muscle_window, text="", font=("Times New Roman", 12))
    lbl_status_muscle.pack(pady=(5, 5))

    def update_muscle_list():
        listbox_muscles.delete(0, 'end')
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM MuscleGroups ORDER BY name ASC")
            for row in cursor.fetchall():
                listbox_muscles.insert('end', row[0])
        except sqlite3.Error:
            listbox_muscles.insert('end', "Error loading muscle groups")
        finally:
            if conn:
                conn.close()

    def save_muscle():
        muscle_name = entry_muscle_name.get().strip()

        if not muscle_name:
            lbl_status_muscle.configure(text="Muscle group name missing.", text_color="#FF6B6B")
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("INSERT INTO MuscleGroups (name) VALUES (?)", (muscle_name,))
            conn.commit()

            lbl_status_muscle.configure(text=f"'{muscle_name}' added successfully!", text_color="green")
            entry_muscle_name.delete(0, 'end')

            update_muscle_list()

        except sqlite3.IntegrityError:
            lbl_status_muscle.configure(text="This muscle group already exists.", text_color="#FF6B6B")
        except sqlite3.Error:
            lbl_status_muscle.configure(text="A database error occurred.", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    btn_save = ctk.CTkButton(muscle_window, text="Add Muscle Group", command=save_muscle, width=250, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_save.pack(pady=(0, 15))

    ctk.CTkFrame(muscle_window, height=2, width=350, fg_color="gray").pack(pady=5)

    ctk.CTkLabel(muscle_window, text="Current Muscle Groups:", font=("Times New Roman", 12)).pack(pady=(5, 5))

    frame_list = ctk.CTkFrame(muscle_window)
    frame_list.pack(pady=5, padx=40, fill="both", expand=True)

    listbox_muscles = tk.Listbox(frame_list, font=("Times New Roman", 14), bg="#2b2b2b", fg="white",
                                 selectbackground="#88D4AB", selectforeground="black", highlightthickness=0,
                                 borderwidth=0)
    listbox_muscles.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)

    scrollbar = ctk.CTkScrollbar(frame_list, command=listbox_muscles.yview)
    scrollbar.pack(side="right", fill="y", padx=5, pady=10)
    listbox_muscles.configure(yscrollcommand=scrollbar.set)

    update_muscle_list()

    def view_muscle_details():
        selection = listbox_muscles.curselection()
        if not selection:
            return

        muscle_name = listbox_muscles.get(selection[0])

        muscle_window.withdraw()
        details_window = ctk.CTkToplevel()
        details_window.title("Muscle Group Details")
        details_window.geometry("500x750")

        def close_details_and_go_back():
            details_window.destroy()
            muscle_window.deiconify()

        details_window.protocol("WM_DELETE_WINDOW", close_details_and_go_back)

        ctk.CTkLabel(details_window, text=muscle_name, font=("Times New Roman", 22, "bold"), text_color="#88D4AB").pack(
            pady=(30, 20))

        ctk.CTkLabel(details_window, text="Coming soon", font=("Times New Roman", 36, "bold")).pack(expand=True)

        ctk.CTkButton(details_window, text="Back to Muscle Groups", command=close_details_and_go_back, width=250,
                      height=35, fg_color="transparent", border_width=2, border_color="#A8E6CF",
                      text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=30)

    def edit_selected_muscle():
        selection = listbox_muscles.curselection()
        if not selection:
            return

        old_name = listbox_muscles.get(selection[0])

        edit_win = ctk.CTkToplevel(muscle_window)
        edit_win.title("Edit Muscle Group")
        edit_win.geometry("300x200")
        edit_win.attributes("-topmost", True)

        ctk.CTkLabel(edit_win, text=f"Edit: {old_name}", font=("Times New Roman", 16, "bold")).pack(pady=(20, 10))
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=5)
        entry_edit.insert(0, old_name)

        def save_edit():
            new_name = entry_edit.get().strip()
            if not new_name or new_name == old_name:
                edit_win.destroy()
                return

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("UPDATE MuscleGroups SET name = ? WHERE name = ?", (new_name, old_name))
                conn.commit()
                lbl_status_muscle.configure(text=f"Renamed to '{new_name}'.", text_color="green")
                update_muscle_list()
            except sqlite3.IntegrityError:
                lbl_status_muscle.configure(text="Name already exists.", text_color="#FF6B6B")
            except sqlite3.Error:
                lbl_status_muscle.configure(text="Database Error.", text_color="#FF6B6B")
            finally:
                if conn:
                    conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save", command=save_edit, fg_color="#A8E6CF", hover_color="#88D4AB",
                      text_color="black").pack(pady=15)

    def delete_selected_muscle():
        selection = listbox_muscles.curselection()
        if not selection:
            return

        muscle_to_delete = listbox_muscles.get(selection[0])

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM MuscleGroups WHERE name = ?", (muscle_to_delete,))
            m_id_row = cursor.fetchone()
            if m_id_row:
                m_id = m_id_row[0]
                cursor.execute("SELECT 1 FROM Workouts WHERE muscle_group_id = ? LIMIT 1", (m_id,))
                if cursor.fetchone():
                    lbl_status_muscle.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return

            cursor.execute("DELETE FROM MuscleGroups WHERE name = ?", (muscle_to_delete,))
            conn.commit()

            lbl_status_muscle.configure(text=f"'{muscle_to_delete}' deleted.", text_color="green")
            update_muscle_list()
        except sqlite3.Error as e:
            lbl_status_muscle.configure(text=f"Error: {e}", text_color="#FF6B6B")
        finally:
            if conn:
                conn.close()

    frame_buttons = ctk.CTkFrame(muscle_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))

    btn_view = ctk.CTkButton(frame_buttons, text="View Details", command=view_muscle_details, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                             text_color="black")
    btn_view.pack(side="left", padx=5)

    btn_edit = ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_muscle, width=130, height=35,
                             font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", hover_color="#E2BE93",
                             text_color="black")
    btn_edit.pack(side="left", padx=5)

    btn_delete = ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_muscle,
                               width=130, height=35, fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                               font=("Times New Roman", 14, "bold"))
    btn_delete.pack(side="left", padx=5)

    btn_back = ctk.CTkButton(muscle_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                             fg_color="transparent", border_width=2, border_color="#A8E6CF",
                             text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
    btn_back.pack(side="bottom", pady=20)


# --- Past Workouts Function ---
def open_past_workouts(user_id, parent_window):
    parent_window.withdraw()
    history_window = ctk.CTkToplevel()
    history_window.title("Past Workouts")
    history_window.geometry("500x750")

    def close_and_go_back():
        history_window.destroy()
        parent_window.deiconify()

    history_window.protocol("WM_DELETE_WINDOW", close_and_go_back)

    ctk.CTkLabel(history_window, text="Workout History", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    scroll_frame = ctk.CTkScrollableFrame(history_window, fg_color="transparent")
    scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def load_history():
        for widget in scroll_frame.winfo_children():
            widget.destroy()

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute('''
                           SELECT date, custom_name
                           FROM Workouts
                           WHERE user_id = ?
                           GROUP BY date
                           ORDER BY substr(date, 7, 4) || substr(date, 4, 2) || substr(date, 1, 2) DESC
                           ''', (user_id,))

            rows = cursor.fetchall()
            if not rows:
                ctk.CTkLabel(scroll_frame, text="No workouts logged yet.", font=("Times New Roman", 14)).pack(pady=20)
                return

            for row in rows:
                date_val = row[0]
                custom_name = row[1]

                if custom_name:
                    display_name = custom_name
                else:
                    cursor.execute('''
                        SELECT m.name, COUNT(s.id) as set_count
                        FROM WorkoutSets s
                        JOIN Workouts w ON s.workout_id = w.id
                        JOIN MuscleGroups m ON w.muscle_group_id = m.id
                        WHERE w.date = ? AND w.user_id = ?
                        GROUP BY m.id
                        ORDER BY set_count DESC
                        LIMIT 1
                    ''', (date_val, user_id))
                    dominant_res = cursor.fetchone()
                    if dominant_res:
                        display_name = f"{dominant_res[0]} Workout"
                    else:
                        display_name = "Empty Workout"

                row_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b", corner_radius=5)
                row_frame.pack(fill="x", pady=5)

                btn_del = ctk.CTkButton(row_frame, text="Delete", width=60, height=28, fg_color="#FFB7B2",
                                        hover_color="#E29C97",
                                        text_color="black", font=("Times New Roman", 12, "bold"),
                                        command=lambda d=date_val: delete_specific_workout(d))
                btn_del.pack(side="right", padx=(5, 15))

                btn_view = ctk.CTkButton(row_frame, text="View", width=60, height=28, fg_color="#A8E6CF",
                                         hover_color="#88D4AB",
                                         text_color="black", font=("Times New Roman", 12, "bold"),
                                         command=lambda d=date_val, n=display_name: view_specific_details(d, n))
                btn_view.pack(side="right", padx=5)

                lbl_date = ctk.CTkLabel(row_frame, text=date_val, font=("Times New Roman", 16, "bold"),
                                        text_color="#88D4AB")
                lbl_date.pack(side="left", padx=(15, 5), pady=10)

                lbl_sep = ctk.CTkLabel(row_frame, text="|", font=("Times New Roman", 16), text_color="gray")
                lbl_sep.pack(side="left", padx=5)

                lbl_name = ctk.CTkLabel(row_frame, text=display_name, font=("Times New Roman", 16, "bold"),
                                        text_color="white", anchor="w")
                lbl_name.pack(side="left", padx=(5, 10), fill="x", expand=True)

        except sqlite3.Error as e:
            print("History Error:", e)
            ctk.CTkLabel(scroll_frame, text="Error loading history.", font=("Times New Roman", 14),
                         text_color="#FF6B6B").pack()
        finally:
            if conn:
                conn.close()

    load_history()

    def delete_specific_workout(target_date):
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM Workouts WHERE user_id = ? AND date = ?", (user_id, target_date))
            w_ids = [row[0] for row in cursor.fetchall()]

            if w_ids:
                placeholders = ','.join('?' for _ in w_ids)
                cursor.execute(f"DELETE FROM WorkoutSets WHERE workout_id IN ({placeholders})", w_ids)
                cursor.execute(f"DELETE FROM Workouts WHERE id IN ({placeholders})", w_ids)
                conn.commit()

            load_history()
        except Exception as e:
            print("Error deleting workout:", e)
        finally:
            if conn:
                conn.close()

    def view_specific_details(current_date, current_name):
        history_window.withdraw()

        details_window = ctk.CTkToplevel()
        details_window.title("Workout Details")
        details_window.geometry("500x750")

        def close_details_and_go_back():
            load_history()
            details_window.destroy()
            history_window.deiconify()

        details_window.protocol("WM_DELETE_WINDOW", close_details_and_go_back)

        frame_edit = ctk.CTkFrame(details_window, fg_color="transparent")
        frame_edit.pack(pady=(20, 10))

        entry_edit_name = ctk.CTkEntry(frame_edit, width=220, font=("Times New Roman", 16, "bold"))
        entry_edit_name.grid(row=0, column=0, padx=5)
        entry_edit_name.insert(0, current_name)

        entry_edit_date = ctk.CTkEntry(frame_edit, width=110, font=("Times New Roman", 14))
        entry_edit_date.grid(row=0, column=1, padx=5)
        entry_edit_date.insert(0, current_date)

        lbl_edit_status = ctk.CTkLabel(details_window, text="", font=("Times New Roman", 12))
        lbl_edit_status.pack(pady=(0, 5))

        def save_info():
            nonlocal current_date
            new_name = entry_edit_name.get().strip()
            new_date_raw = entry_edit_date.get().strip()

            if not new_name or not new_date_raw:
                lbl_edit_status.configure(text="Name and Date missing.", text_color="#FF6B6B")
                return

            try:
                parsed = datetime.datetime.strptime(new_date_raw, "%d/%m/%Y").date()
                new_date = parsed.strftime("%d/%m/%Y")
            except ValueError:
                lbl_edit_status.configure(text="Invalid date (DD/MM/YYYY).", text_color="#FF6B6B")
                return

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()

                cursor.execute("UPDATE Workouts SET date = ?, custom_name = ? WHERE user_id = ? AND date = ?",
                               (new_date, new_name, user_id, current_date))
                conn.commit()

                lbl_edit_status.configure(text="Saved successfully!", text_color="green")
                current_date = new_date
                render_details()

            except sqlite3.Error as e:
                lbl_edit_status.configure(text="Database Error.", text_color="#FF6B6B")
            finally:
                if conn:
                    conn.close()

        btn_save_info = ctk.CTkButton(frame_edit, text="Save", width=70, command=save_info,
                                      font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                                      text_color="black")
        btn_save_info.grid(row=0, column=2, padx=5)

        scroll_frame_details = ctk.CTkScrollableFrame(details_window, fg_color="transparent")
        scroll_frame_details.pack(fill="both", expand=True, padx=20, pady=10)

        def delete_set(set_id):
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM WorkoutSets WHERE id = ?", (set_id,))

                cursor.execute("""
                               DELETE
                               FROM Workouts
                               WHERE id NOT IN (SELECT DISTINCT workout_id FROM WorkoutSets)
                               """)
                conn.commit()
            except Exception as e:
                print("Error deleting set:", e)
            finally:
                if conn:
                    conn.close()

            render_details()

        def render_details():
            for widget in scroll_frame_details.winfo_children():
                widget.destroy()

            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute('''
                               SELECT s.id, m.name, e.exercise_name, eq.name, s.reps, s.weight_kg, eq.requires_weight
                               FROM WorkoutSets s
                                        JOIN Workouts w ON s.workout_id = w.id
                                        JOIN Exercises e ON s.exercise_id = e.id
                                        JOIN Equipment eq ON s.equipment_id = eq.id
                                        JOIN MuscleGroups m ON w.muscle_group_id = m.id
                               WHERE w.user_id = ?
                                 AND w.date = ?
                               ORDER BY m.name ASC, e.exercise_name ASC, eq.name ASC, s.id ASC
                               ''', (user_id, current_date))

                sets = cursor.fetchall()

                if not sets:
                    ctk.CTkLabel(scroll_frame_details, text="No sets recorded for this date.",
                                 font=("Times New Roman", 14)).pack(pady=20)
                    return

                current_muscle = ""
                current_exercise = ""
                current_equipment = ""
                set_num = 1

                for row in sets:
                    set_id, muscle_name, ex_name, eq_name, reps, weight, req_weight = row

                    if muscle_name != current_muscle:
                        current_muscle = muscle_name
                        ctk.CTkLabel(scroll_frame_details, text=f"--- {muscle_name} ---",
                                     font=("Times New Roman", 20, "bold"),
                                     text_color="#FFB7B2").pack(anchor="w", pady=(15, 5))
                        current_exercise = ""
                        current_equipment = ""

                    if ex_name != current_exercise or eq_name != current_equipment:
                        current_exercise = ex_name
                        current_equipment = eq_name
                        set_num = 1
                        ctk.CTkLabel(scroll_frame_details, text=f"{ex_name} ({eq_name})",
                                     font=("Times New Roman", 16, "bold")).pack(
                            anchor="w", pady=(10, 2), padx=10)

                    # --- Intelligent History Display Logic ---
                    # Safely ensure weight is read as a float (handles legacy nulls/strings if any exist)
                    try:
                        weight_float = float(weight) if weight else 0.0
                    except ValueError:
                        weight_float = 0.0

                    if ex_name == "Abs" and reps == 1:
                        set_text = "Completed"
                    elif weight_float == 0.0:
                        set_text = f"Set {set_num}: {reps:g} reps"
                    else:
                        set_text = f"Set {set_num}: {reps:g} reps @ {weight_float:g}kg"

                    set_frame = ctk.CTkFrame(scroll_frame_details, fg_color="transparent")
                    set_frame.pack(fill="x", padx=30, pady=2)

                    ctk.CTkLabel(set_frame, text=set_text, font=("Times New Roman", 14)).pack(side="left")

                    btn_del_set = ctk.CTkButton(set_frame, text="X", width=24, height=24,
                                                fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                                                command=lambda sid=set_id: delete_set(sid))
                    btn_del_set.pack(side="right")

                    set_num += 1

            except sqlite3.Error:
                ctk.CTkLabel(scroll_frame_details, text="Error loading details.", text_color="#FF6B6B").pack()
            finally:
                if conn:
                    conn.close()

        render_details()

        ctk.CTkButton(details_window, text="Back to History", command=close_details_and_go_back, width=250, height=35,
                      fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=20)

    btn_back = ctk.CTkButton(history_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                             fg_color="transparent", border_width=2, border_color="#A8E6CF",
                             text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
    btn_back.pack(side="bottom", pady=20)


# --- Dashboard Function ---
def open_dashboard(user_id):
    app.withdraw()

    dashboard = ctk.CTkToplevel()
    dashboard.title("Gym Tracker - Dashboard")
    dashboard.geometry("500x750")

    dashboard.protocol("WM_DELETE_WINDOW", app.destroy)

    label_welcome = ctk.CTkLabel(dashboard, text="Gym Tracker", font=("Times New Roman", 28, "bold"))
    label_welcome.pack(pady=(40, 20))

    btn_new_workout = ctk.CTkButton(dashboard, text="Log a Workout", height=50, width=250,
                                    font=("Times New Roman", 16, "bold"),
                                    command=lambda: open_new_workout(user_id, dashboard), fg_color="#A8E6CF",
                                    hover_color="#88D4AB", text_color="black")
    btn_new_workout.pack(pady=10)

    btn_exercises = ctk.CTkButton(dashboard, text="Exercises", height=50, width=250,
                                  font=("Times New Roman", 16, "bold"),
                                  command=lambda: open_exercises_window(user_id, dashboard), fg_color="#A8E6CF",
                                  hover_color="#88D4AB", text_color="black")
    btn_exercises.pack(pady=10)

    btn_equip = ctk.CTkButton(dashboard, text="Equipment", height=50, width=250, font=("Times New Roman", 16, "bold"),
                              command=lambda: open_equipment_window(user_id, dashboard), fg_color="#A8E6CF",
                              hover_color="#88D4AB", text_color="black")
    btn_equip.pack(pady=10)

    btn_muscle_groups = ctk.CTkButton(dashboard, text="Muscle Groups", height=50, width=250,
                                      font=("Times New Roman", 16, "bold"),
                                      command=lambda: open_muscle_groups_window(user_id, dashboard), fg_color="#A8E6CF",
                                      hover_color="#88D4AB", text_color="black")
    btn_muscle_groups.pack(pady=10)

    btn_history = ctk.CTkButton(dashboard, text="Workout History", height=50, width=250,
                                font=("Times New Roman", 16, "bold"),
                                command=lambda: open_past_workouts(user_id, dashboard), fg_color="#A8E6CF",
                                hover_color="#88D4AB", text_color="black")
    btn_history.pack(pady=10)

    def logout():
        dashboard.destroy()
        entry_password.delete(0, 'end')
        lbl_status.configure(text="")
        app.deiconify()

    btn_logout = ctk.CTkButton(dashboard, text="Back to Login", command=logout, width=250, height=35,
                               fg_color="transparent", border_width=2, border_color="#A8E6CF",
                               text_color=("black", "white"),
                               font=("Times New Roman", 14, "bold"))
    btn_logout.pack(pady=(20, 10))

    btn_exit_dash = ctk.CTkButton(dashboard, text="Exit Application", command=app.destroy, width=250, height=35,
                                  fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                                  font=("Times New Roman", 14, "bold"))
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
        cursor.execute("INSERT INTO Users (username, password_hash) VALUES (?, ?)",
                       (username, hashed_password.decode('utf-8')))
        conn.commit()

        lbl_status.configure(text="Account created! You can now log in.", text_color="green")
        entry_password.delete(0, 'end')
    except sqlite3.IntegrityError:
        lbl_status.configure(text="Username taken", text_color="#FF6B6B")
    finally:
        if conn:
            conn.close()


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

        if result:
            user_id = result[0]
            stored_hash = result[1].encode('utf-8')

            if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                lbl_status.configure(text="")
                open_dashboard(user_id)
            else:
                lbl_status.configure(text="Username or Password invalid", text_color="#FF6B6B")
        else:
            lbl_status.configure(text="Username or Password invalid", text_color="#FF6B6B")
    except sqlite3.Error:
        lbl_status.configure(text="Database Error", text_color="#FF6B6B")
    finally:
        if conn:
            conn.close()


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

btn_login = ctk.CTkButton(app, text="Login", command=login_user, width=250, height=35,
                          font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                          text_color="black")
btn_login.pack(pady=(10, 10))

btn_register = ctk.CTkButton(app, text="Register", command=register_user, width=250, height=35, fg_color="transparent",
                             border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                             font=("Times New Roman", 14, "bold"))
btn_register.pack(pady=10)

btn_exit = ctk.CTkButton(app, text="Exit Application", command=app.destroy, width=250, height=35, fg_color="#FFB7B2",
                         hover_color="#E29C97", text_color="black", font=("Times New Roman", 14, "bold"))
btn_exit.pack(pady=10)

if __name__ == "__main__":
    app.mainloop()