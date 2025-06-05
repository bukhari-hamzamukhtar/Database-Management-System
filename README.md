# Class Management System

This is a simple class management system built with Python's `tkinter` for the GUI and PostgreSQL for the backend. It allows toggling between **student** and **teacher** views with full CRUD functionality, including an **undo delete** feature using backup tables.

## Features

- Toggle between **Student** and **Teacher** views
- Insert, update, delete, and undo-delete records
- Uses backup tables to enable undo functionality

## File Overview

- `main.py` — GUI logic and database interaction
- `database.py` — Handles PostgreSQL connection setup using credentials from `database.ini`
- `database.ini` — Contains connection parameters (host, dbname, user, password)
- `tables.sql` — Schema definitions for `student`, `teacher`, `student_backup`, and `teachers_backup`
- `__pycache__/` — Auto-generated; **not included** in version control (see `.gitignore`)

## Setup Instructions

1. **Clone the repo**
2. Set up your PostgreSQL database using `tables.sql`
3. Edit `database.ini` with your DB credentials

## To Run Application
   ```bash
   python main.py
