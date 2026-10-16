import customtkinter as ctk
import sqlite3
import datetime
from settings import DB_PATH


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

    ctk.CTkLabel(workout_window, text="Log a Workout", font=("Times New Roman", 24, "bold")).pack(pady=(20, 10))

    ctk.CTkLabel(workout_window, text="Date (DD/MM/YYYY):", font=("Times New Roman", 12)).pack(pady=(5, 0))
    entry_date = ctk.CTkEntry(workout_window, width=250, font=("Times New Roman", 12))
    entry_date.pack()
    entry_date.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

    lbl_error_date = ctk.CTkLabel(workout_window, text="", font=("Times New Roman", 12), text_color="#FF6B6B")
    lbl_error_date.pack(pady=(0, 5))

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
            cursor.execute(
                '''SELECT e.exercise_name FROM Exercises e JOIN MuscleGroups m ON e.muscle_group_id = m.id WHERE m.name = ? ORDER BY e.exercise_name ASC''',
                (selected_muscle,))
            results = [row[0] for row in cursor.fetchall()]
            combo_exercise.configure(values=results if results else ["(No exercises found)"])
            combo_exercise.set("")
        except sqlite3.Error:
            combo_exercise.configure(values=["(Error)"])
        finally:
            if conn:
                conn.close()

    ctk.CTkLabel(workout_window, text="Muscle Group Worked:", font=("Times New Roman", 12)).pack(pady=(5, 0))
    muscle_groups = get_muscle_groups()
    combo_muscle = ctk.CTkOptionMenu(workout_window, values=muscle_groups, command=on_muscle_change, width=250,
                                     fg_color="#A8E6CF", button_color="#88D4AB", button_hover_color="#7AC29A",
                                     text_color="black")
    combo_muscle.set("")
    combo_muscle.pack()

    def on_equipment_change(choice):
        pass

    ctk.CTkLabel(workout_window, text="Equipment Used:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    equipment_types = get_equipment()
    combo_equipment = ctk.CTkOptionMenu(workout_window, values=equipment_types, command=on_equipment_change, width=250,
                                        fg_color="#A8E6CF", button_color="#88D4AB", button_hover_color="#7AC29A",
                                        text_color="black")
    combo_equipment.set("")
    combo_equipment.pack()

    def on_exercise_change(choice):
        current_set.set(1)
        lbl_current_set.configure(text="Recording a set")

    ctk.CTkLabel(workout_window, text="Exercise:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    combo_exercise = ctk.CTkOptionMenu(workout_window, values=["(Select muscle group first)"], width=250,
                                       command=on_exercise_change, fg_color="#A8E6CF", button_color="#88D4AB",
                                       button_hover_color="#7AC29A", text_color="black")
    combo_exercise.set("")
    combo_exercise.pack()

    lbl_error_dropdowns = ctk.CTkLabel(workout_window, text="", font=("Times New Roman", 12), text_color="#FF6B6B")
    lbl_error_dropdowns.pack(pady=(5, 0))

    ctk.CTkFrame(workout_window, height=2, width=400, fg_color="gray").pack(pady=10)

    lbl_current_set = ctk.CTkLabel(workout_window, text="Recording a set", font=("Times New Roman", 18, "bold"),
                                   text_color="#88D4AB")
    lbl_current_set.pack(pady=(0, 10))

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

        invalid_selections = ["", "(No data)", "(Database Error)", "(Select muscle group first)",
                              "(No exercises found)", "(Error)"]
        if muscle in invalid_selections or ex_name in invalid_selections or equip in invalid_selections:
            lbl_error_dropdowns.configure(text="Dropdown selection missing")
            has_error = True

        sets_count, reps_val, weight_val = 1, 0, 0.0

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

        if has_error: return

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

            for _ in range(sets_count):
                cursor.execute(
                    '''INSERT INTO WorkoutSets (workout_id, exercise_id, equipment_id, weight_kg, reps) VALUES (?, ?, ?, ?, ?)''',
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

    ctk.CTkButton(workout_window, text="Add Set(s)", command=add_set, width=250, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                  text_color="black").pack(pady=(10, 15))
    ctk.CTkButton(workout_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                  fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                  font=("Times New Roman", 14, "bold")).pack(pady=(5, 10))


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
        for widget in scroll_frame.winfo_children(): widget.destroy()
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT date, custom_name FROM Workouts WHERE user_id = ? GROUP BY date ORDER BY substr(date, 7, 4) || substr(date, 4, 2) || substr(date, 1, 2) DESC''',
                (user_id,))
            rows = cursor.fetchall()

            if not rows:
                ctk.CTkLabel(scroll_frame, text="No workouts logged yet.", font=("Times New Roman", 14)).pack(pady=20)
                return

            for row in rows:
                date_val, custom_name = row[0], row[1]
                if custom_name:
                    display_name = custom_name
                else:
                    cursor.execute(
                        '''SELECT m.name, COUNT(s.id) as set_count FROM WorkoutSets s JOIN Workouts w ON s.workout_id = w.id JOIN MuscleGroups m ON w.muscle_group_id = m.id WHERE w.date = ? AND w.user_id = ? GROUP BY m.id ORDER BY set_count DESC LIMIT 1''',
                        (date_val, user_id))
                    dominant_res = cursor.fetchone()
                    display_name = f"{dominant_res[0]} Workout" if dominant_res else "Empty Workout"

                row_frame = ctk.CTkFrame(scroll_frame, fg_color="#2b2b2b", corner_radius=5)
                row_frame.pack(fill="x", pady=5)

                ctk.CTkButton(row_frame, text="Delete", width=60, height=28, fg_color="#FFB7B2", hover_color="#E29C97",
                              text_color="black", font=("Times New Roman", 12, "bold"),
                              command=lambda d=date_val: delete_specific_workout(d)).pack(side="right", padx=(5, 15))
                ctk.CTkButton(row_frame, text="View", width=60, height=28, fg_color="#A8E6CF", hover_color="#88D4AB",
                              text_color="black", font=("Times New Roman", 12, "bold"),
                              command=lambda d=date_val, n=display_name: view_specific_details(d, n)).pack(side="right",
                                                                                                           padx=5)
                ctk.CTkLabel(row_frame, text=date_val, font=("Times New Roman", 16, "bold"), text_color="#88D4AB").pack(
                    side="left", padx=(15, 5), pady=10)
                ctk.CTkLabel(row_frame, text="|", font=("Times New Roman", 16), text_color="gray").pack(side="left",
                                                                                                        padx=5)
                ctk.CTkLabel(row_frame, text=display_name, font=("Times New Roman", 16, "bold"), text_color="white",
                             anchor="w").pack(side="left", padx=(5, 10), fill="x", expand=True)

        except sqlite3.Error as e:
            ctk.CTkLabel(scroll_frame, text="Error loading history.", font=("Times New Roman", 14),
                         text_color="#FF6B6B").pack()
        finally:
            if conn: conn.close()

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
        except Exception:
            pass
        finally:
            if conn: conn.close()

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
            new_name, new_date_raw = entry_edit_name.get().strip(), entry_edit_date.get().strip()
            if not new_name or not new_date_raw:
                lbl_edit_status.configure(text="Name and Date missing.", text_color="#FF6B6B")
                return
            try:
                parsed = datetime.datetime.strptime(new_date_raw, "%d/%m/%Y").date()
                new_date = parsed.strftime("%d/%m/%Y")
            except ValueError:
                lbl_edit_status.configure(text="Invalid date format.", text_color="#FF6B6B")
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
            except sqlite3.Error:
                lbl_edit_status.configure(text="Database Error.", text_color="#FF6B6B")
            finally:
                if conn: conn.close()

        ctk.CTkButton(frame_edit, text="Save", width=70, command=save_info, font=("Times New Roman", 14, "bold"),
                      fg_color="#A8E6CF", hover_color="#88D4AB", text_color="black").grid(row=0, column=2, padx=5)
        scroll_frame_details = ctk.CTkScrollableFrame(details_window, fg_color="transparent")
        scroll_frame_details.pack(fill="both", expand=True, padx=20, pady=10)

        def delete_set(set_id):
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("DELETE FROM WorkoutSets WHERE id = ?", (set_id,))
                cursor.execute("DELETE FROM Workouts WHERE id NOT IN (SELECT DISTINCT workout_id FROM WorkoutSets)")
                conn.commit()
            except Exception:
                pass
            finally:
                if conn: conn.close()
            render_details()

        def render_details():
            for widget in scroll_frame_details.winfo_children(): widget.destroy()
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute(
                    '''SELECT s.id, m.name, e.exercise_name, eq.name, s.reps, s.weight_kg FROM WorkoutSets s JOIN Workouts w ON s.workout_id = w.id JOIN Exercises e ON s.exercise_id = e.id JOIN Equipment eq ON s.equipment_id = eq.id JOIN MuscleGroups m ON w.muscle_group_id = m.id WHERE w.user_id = ? AND w.date = ? ORDER BY m.name ASC, e.exercise_name ASC, eq.name ASC, s.id ASC''',
                    (user_id, current_date))
                sets = cursor.fetchall()
                if not sets:
                    ctk.CTkLabel(scroll_frame_details, text="No sets recorded for this date.",
                                 font=("Times New Roman", 14)).pack(pady=20)
                    return

                current_muscle, current_exercise, current_equipment, set_num = "", "", "", 1

                for row in sets:
                    set_id, muscle_name, ex_name, eq_name, reps, weight = row

                    if muscle_name != current_muscle:
                        current_muscle = muscle_name
                        ctk.CTkLabel(scroll_frame_details, text=f"--- {muscle_name} ---",
                                     font=("Times New Roman", 20, "bold"), text_color="#FFB7B2").pack(anchor="w",
                                                                                                      pady=(15, 5))
                        current_exercise, current_equipment = "", ""

                    if ex_name != current_exercise or eq_name != current_equipment:
                        current_exercise, current_equipment, set_num = ex_name, eq_name, 1
                        ctk.CTkLabel(scroll_frame_details, text=f"{ex_name} ({eq_name})",
                                     font=("Times New Roman", 16, "bold")).pack(anchor="w", pady=(10, 2), padx=10)

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
                    ctk.CTkButton(set_frame, text="X", width=24, height=24, fg_color="#FFB7B2", hover_color="#E29C97",
                                  text_color="black", command=lambda sid=set_id: delete_set(sid)).pack(side="right")
                    set_num += 1
            finally:
                if conn: conn.close()

        render_details()
        ctk.CTkButton(details_window, text="Back to History", command=close_details_and_go_back, width=250, height=35,
                      fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=20)

    ctk.CTkButton(history_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                  fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                  font=("Times New Roman", 14, "bold")).pack(side="bottom", pady=20)