import sqlite3
import os
import sys


# --- Path Helper ---
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


DB_PATH = resource_path('gym_tracker.db')


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # 1. Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')

    # 2. Create MuscleGroups table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MuscleGroups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # 3. Create Workouts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            date TEXT NOT NULL,
            muscle_group_id INTEGER,
            custom_name TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
            FOREIGN KEY (muscle_group_id) REFERENCES MuscleGroups(id) ON DELETE RESTRICT
        )
    ''')

    # 4. Create Exercises table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT UNIQUE NOT NULL,
            muscle_group_id INTEGER,
            FOREIGN KEY (muscle_group_id) REFERENCES MuscleGroups(id) ON DELETE CASCADE
        )
    ''')

    # 5. Create Equipment table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Equipment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            requires_weight INTEGER DEFAULT 0
        )
    ''')

    # 6. Create WorkoutSets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS WorkoutSets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            exercise_id INTEGER,
            equipment_id INTEGER,
            weight_kg REAL NOT NULL,
            reps INTEGER NOT NULL,
            FOREIGN KEY (workout_id) REFERENCES Workouts(id) ON DELETE CASCADE,
            FOREIGN KEY (exercise_id) REFERENCES Exercises(id) ON DELETE RESTRICT,
            FOREIGN KEY (equipment_id) REFERENCES Equipment(id) ON DELETE RESTRICT
        )
    ''')

    # 7. AUTOMATED TRIGGER
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS auto_delete_empty_workouts
        AFTER DELETE ON WorkoutSets
        BEGIN
            DELETE FROM Workouts 
            WHERE id = OLD.workout_id 
            AND NOT EXISTS (SELECT 1 FROM WorkoutSets WHERE workout_id = OLD.workout_id);
        END;
    ''')

    # --- Pre-populate the Libraries with Defaults ---

    # Updated Muscle Groups
    default_muscles = [
        ('Back',), ('Biceps',), ('Chest',), ('Core',),
        ('Forearms',), ('Legs',), ('Shoulders',), ('Triceps',)
    ]
    cursor.executemany('INSERT OR IGNORE INTO MuscleGroups (name) VALUES (?)', default_muscles)

    # Updated Equipment (I assigned '1' to Disc since it requires weight input)
    default_equipment = [
        ('Barbell', 1),
        ('Bodyweight', 1),
        ('Cable', 0),
        ('Disc', 1),
        ('Dumbbell', 1),
        ('Machine', 0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO Equipment (name, requires_weight) VALUES (?, ?)', default_equipment)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables()
    print(f"Database and tables created successfully at: {DB_PATH}")