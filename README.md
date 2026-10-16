# Gym Tracker

Gym Tracker is a Python-based desktop application designed for logging workouts, tracking progress, and managing fitness routines. Built with `customtkinter` for a modern user interface and SQLite for robust local data storage, the application operates as a standalone, portable executable. It adapts dynamically to user input, offering custom exercise libraries, intelligent equipment logic, and automated workout categorization.

##  Key Features

*   **Secure Local Accounts:** User authentication powered by `bcrypt` ensures personal data remains private and secure on your local machine.
*   **Dynamic Workout Logging:** Create and manage custom muscle groups, exercises, and equipment. The interface smartly ties exercises to specific muscle groups and logs detailed set data.
*   **Smart History Tracking:** A chronological, scrollable timeline that automatically names daily workouts based on the dominant muscle group targeted that day, with full editing capabilities.
*   **Relational Database:** Features strict SQL `CASCADE` and `RESTRICT` rules to prevent ghost data and automatically clean up empty workouts.
*   **Fully Portable:** Designed to be packaged as a single executable file paired with a local `.db` file, allowing for easy data backups and portability across Windows machines without complex installations.

##  Requirements & Usage

To run this project from the source code, you need Python installed along with the following libraries:

```bash
pip install customtkinter bcrypt
```
To start the application, run:
```
python main.py
```
