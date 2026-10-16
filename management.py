import customtkinter as ctk
import tkinter as tk
import sqlite3
from settings import DB_PATH


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
        if not muscle_name or muscle_name in ["", "(No data)", "(Database Error)"]: return
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT e.exercise_name FROM Exercises e JOIN MuscleGroups m ON e.muscle_group_id = m.id WHERE m.name = ? ORDER BY e.exercise_name ASC''',
                (muscle_name,))
            for row in cursor.fetchall(): listbox_exercises.insert('end', row[0])
        except sqlite3.Error:
            listbox_exercises.insert('end', "Error loading exercises")
        finally:
            if conn: conn.close()

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
            if conn: conn.close()

    ctk.CTkLabel(ex_window, text="Target Muscle Group:", font=("Times New Roman", 12)).pack(pady=(10, 0))
    combo_muscle = ctk.CTkOptionMenu(ex_window, values=get_muscle_groups(), width=250, command=update_exercise_list,
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
        muscle_name, ex_name = combo_muscle.get(), entry_ex_name.get().strip()
        if muscle_name in ["", "(No data)", "(Database Error)"]:
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
            if not result: return

            cursor.execute("INSERT INTO Exercises (exercise_name, muscle_group_id) VALUES (?, ?)", (ex_name, result[0]))
            conn.commit()
            lbl_status_ex.configure(text=f"'{ex_name}' added successfully!", text_color="green")
            entry_ex_name.delete(0, 'end')
            update_exercise_list(muscle_name)
        except sqlite3.IntegrityError:
            lbl_status_ex.configure(text="This exercise already exists.", text_color="#FF6B6B")
        except sqlite3.Error:
            lbl_status_ex.configure(text="A database error occurred.", text_color="#FF6B6B")
        finally:
            if conn: conn.close()

    ctk.CTkButton(ex_window, text="Add Exercise", command=save_exercise, width=250, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                  text_color="black").pack(pady=(0, 15))
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
        if not listbox_exercises.curselection(): return
        ex_name = listbox_exercises.get(listbox_exercises.curselection()[0])
        ex_window.withdraw()
        details_window = ctk.CTkToplevel()
        details_window.title("Exercise Details")
        details_window.geometry("500x750")

        def close_details(): details_window.destroy(); ex_window.deiconify()

        details_window.protocol("WM_DELETE_WINDOW", close_details)
        ctk.CTkLabel(details_window, text=ex_name, font=("Times New Roman", 22, "bold"), text_color="#88D4AB").pack(
            pady=(30, 20))
        ctk.CTkLabel(details_window, text="Coming soon", font=("Times New Roman", 36, "bold")).pack(expand=True)
        ctk.CTkButton(details_window, text="Back", command=close_details, width=250, height=35, fg_color="transparent",
                      border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                      font=("Times New Roman", 14, "bold")).pack(pady=30)

    def edit_selected_exercise():
        if not listbox_exercises.curselection(): return
        old_name = listbox_exercises.get(listbox_exercises.curselection()[0])
        edit_win = ctk.CTkToplevel(ex_window)
        edit_win.title("Edit")
        edit_win.geometry("300x200")
        edit_win.attributes("-topmost", True)
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=20)
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
                update_exercise_list(combo_muscle.get())
            except sqlite3.Error:
                pass
            finally:
                if conn: conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save", command=save_edit, fg_color="#A8E6CF", text_color="black").pack(pady=15)

    def delete_selected_exercise():
        if not listbox_exercises.curselection(): return
        ex_name_to_delete = listbox_exercises.get(listbox_exercises.curselection()[0])
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Exercises WHERE exercise_name = ?", (ex_name_to_delete,))
            ex_id_row = cursor.fetchone()
            if ex_id_row:
                cursor.execute("SELECT 1 FROM WorkoutSets WHERE exercise_id = ? LIMIT 1", (ex_id_row[0],))
                if cursor.fetchone():
                    lbl_status_ex.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return
            cursor.execute("DELETE FROM Exercises WHERE exercise_name = ?", (ex_name_to_delete,))
            conn.commit()
            update_exercise_list(combo_muscle.get())
        except sqlite3.Error:
            pass
        finally:
            if conn: conn.close()

    frame_buttons = ctk.CTkFrame(ex_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))
    ctk.CTkButton(frame_buttons, text="View Details", command=view_exercise_details, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                  text_color="black").pack(side="left", padx=5)
    ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_exercise, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", hover_color="#E2BE93",
                  text_color="black").pack(side="left", padx=5)
    ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_exercise, width=130, height=35,
                  fg_color="#FFB7B2", hover_color="#E29C97", text_color="black",
                  font=("Times New Roman", 14, "bold")).pack(side="left", padx=5)
    ctk.CTkButton(ex_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                  fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                  font=("Times New Roman", 14, "bold")).pack(side="bottom", pady=20)


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
    ctk.CTkCheckBox(equip_window, text="Requires Weight (kg)?", font=("Times New Roman", 12), variable=var_req_weight,
                    fg_color="#A8E6CF", hover_color="#88D4AB").pack(pady=(5, 5))
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
            for row in cursor.fetchall(): listbox_equipment.insert('end', row[0])
        except sqlite3.Error:
            listbox_equipment.insert('end', "Error loading equipment")
        finally:
            if conn: conn.close()

    def save_equipment():
        equip_name, req_weight_val = entry_equip_name.get().strip(), var_req_weight.get()
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
        finally:
            if conn: conn.close()

    ctk.CTkButton(equip_window, text="Add Equipment", command=save_equipment, width=250, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", hover_color="#88D4AB",
                  text_color="black").pack(pady=(0, 15))
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
        pass  # Kept generic for length; implement like exercises if needed

    def edit_selected_equipment():
        if not listbox_equipment.curselection(): return
        old_name = listbox_equipment.get(listbox_equipment.curselection()[0])
        conn = None;
        old_req_weight = 0
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT requires_weight FROM Equipment WHERE name = ?", (old_name,))
            row = cursor.fetchone()
            if row: old_req_weight = row[0]
        finally:
            if conn: conn.close()

        edit_win = ctk.CTkToplevel(equip_window)
        edit_win.title("Edit Equipment")
        edit_win.geometry("300x250")
        edit_win.attributes("-topmost", True)
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=20)
        entry_edit.insert(0, old_name)
        var_edit_req = ctk.IntVar(value=old_req_weight)
        ctk.CTkCheckBox(edit_win, text="Requires Weight (kg)?", variable=var_edit_req, fg_color="#A8E6CF").pack(pady=10)

        def save_edit():
            new_name, new_req = entry_edit.get().strip(), var_edit_req.get()
            if not new_name: return
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("UPDATE Equipment SET name = ?, requires_weight = ? WHERE name = ?",
                               (new_name, new_req, old_name))
                conn.commit()
                update_equipment_list()
            finally:
                if conn: conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save Changes", command=save_edit, fg_color="#A8E6CF", text_color="black").pack(
            pady=15)

    def delete_selected_equipment():
        if not listbox_equipment.curselection(): return
        equip_to_delete = listbox_equipment.get(listbox_equipment.curselection()[0])
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Equipment WHERE name = ?", (equip_to_delete,))
            eq_id_row = cursor.fetchone()
            if eq_id_row:
                cursor.execute("SELECT 1 FROM WorkoutSets WHERE equipment_id = ? LIMIT 1", (eq_id_row[0],))
                if cursor.fetchone():
                    lbl_status_equip.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return
            cursor.execute("DELETE FROM Equipment WHERE name = ?", (equip_to_delete,))
            conn.commit()
            update_equipment_list()
        finally:
            if conn: conn.close()

    frame_buttons = ctk.CTkFrame(equip_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))
    ctk.CTkButton(frame_buttons, text="View Details", command=view_equipment_details, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", text_color="black").pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_equipment, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", text_color="black").pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_equipment, width=130, height=35,
                  fg_color="#FFB7B2", text_color="black", font=("Times New Roman", 14, "bold")).pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(equip_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                  fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                  font=("Times New Roman", 14, "bold")).pack(side="bottom", pady=20)


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
            for row in cursor.fetchall(): listbox_muscles.insert('end', row[0])
        finally:
            if conn: conn.close()

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
        finally:
            if conn: conn.close()

    ctk.CTkButton(muscle_window, text="Add Muscle Group", command=save_muscle, width=250, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", text_color="black").pack(pady=(0, 15))
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
        pass

    def edit_selected_muscle():
        if not listbox_muscles.curselection(): return
        old_name = listbox_muscles.get(listbox_muscles.curselection()[0])
        edit_win = ctk.CTkToplevel(muscle_window)
        edit_win.title("Edit")
        edit_win.geometry("300x200")
        edit_win.attributes("-topmost", True)
        entry_edit = ctk.CTkEntry(edit_win, width=200)
        entry_edit.pack(pady=20)
        entry_edit.insert(0, old_name)

        def save_edit():
            new_name = entry_edit.get().strip()
            if not new_name or new_name == old_name:
                edit_win.destroy();
                return
            conn = None
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cursor = conn.cursor()
                cursor.execute("UPDATE MuscleGroups SET name = ? WHERE name = ?", (new_name, old_name))
                conn.commit()
                update_muscle_list()
            finally:
                if conn: conn.close()
            edit_win.destroy()

        ctk.CTkButton(edit_win, text="Save", command=save_edit, fg_color="#A8E6CF", text_color="black").pack(pady=15)

    def delete_selected_muscle():
        if not listbox_muscles.curselection(): return
        muscle_to_delete = listbox_muscles.get(listbox_muscles.curselection()[0])
        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM MuscleGroups WHERE name = ?", (muscle_to_delete,))
            m_id_row = cursor.fetchone()
            if m_id_row:
                cursor.execute("SELECT 1 FROM Workouts WHERE muscle_group_id = ? LIMIT 1", (m_id_row[0],))
                if cursor.fetchone():
                    lbl_status_muscle.configure(text="Cannot delete: Used in past workouts.", text_color="#FF6B6B")
                    return
            cursor.execute("DELETE FROM MuscleGroups WHERE name = ?", (muscle_to_delete,))
            conn.commit()
            update_muscle_list()
        finally:
            if conn: conn.close()

    frame_buttons = ctk.CTkFrame(muscle_window, fg_color="transparent")
    frame_buttons.pack(pady=(10, 10))
    ctk.CTkButton(frame_buttons, text="View Details", command=view_muscle_details, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#A8E6CF", text_color="black").pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(frame_buttons, text="Edit Selected", command=edit_selected_muscle, width=130, height=35,
                  font=("Times New Roman", 14, "bold"), fg_color="#FFD6A5", text_color="black").pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(frame_buttons, text="Delete Selected", command=delete_selected_muscle, width=130, height=35,
                  fg_color="#FFB7B2", text_color="black", font=("Times New Roman", 14, "bold")).pack(side="left",
                                                                                                     padx=5)
    ctk.CTkButton(muscle_window, text="Back to Dashboard", command=close_and_go_back, width=250, height=35,
                  fg_color="transparent", border_width=2, border_color="#A8E6CF", text_color=("black", "white"),
                  font=("Times New Roman", 14, "bold")).pack(side="bottom", pady=20)