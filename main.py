import tkinter as tk
from tkinter import ttk, messagebox
from database import get_connection

class University:
    def __init__(self, root):
        self.root = root
        self.root.title("Class Management System")
        self.root.geometry("800x550")
        self.root.configure(bg="#f0f4f8")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#f0f4f8")
        self.style.configure("TButton", padding=6, relief="flat", background="#4a90e2", foreground="white")
        self.style.configure("Treeview", background="#ffffff", foreground="#333333", fieldbackground="#ffffff", rowheight=25)
        self.style.map("TButton", background=[("active", "#357ABD")])
        self.style.configure("TLabel", background="#f0f4f8", font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.current_view = "students"
        self.form_entries = {}

        self.setup_ui()
        self.switch_view("students")

    def setup_ui(self):
        toggle_frame = ttk.Frame(self.root)
        toggle_frame.pack(pady=15)

        self.student_btn = ttk.Button(toggle_frame, text="Students View", command=self.load_students_view)
        self.student_btn.grid(row=0, column=0, padx=10)

        self.teacher_btn = ttk.Button(toggle_frame, text="Teachers View", command=self.load_teachers_view)
        self.teacher_btn.grid(row=0, column=1, padx=10)

        self.form_frame = ttk.Frame(self.root)
        self.form_frame.pack(pady=10)

        self.build_form()

        crud_frame = ttk.Frame(self.root)
        crud_frame.pack(pady=15)

        self.insert_btn = ttk.Button(crud_frame, text="Insert", command=self.insert_record)
        self.insert_btn.grid(row=0, column=0, padx=10)

        self.update_btn = ttk.Button(crud_frame, text="Update", command=self.update_record)
        self.update_btn.grid(row=0, column=1, padx=10)

        self.delete_btn = ttk.Button(crud_frame, text="Delete", command=self.delete_record)
        self.delete_btn.grid(row=0, column=2, padx=10)

        self.undo_btn = ttk.Button(crud_frame, text="Undo Delete", command=self.undo_delete)
        self.undo_btn.grid(row=0, column=3, padx=10)

        self.tree = ttk.Treeview(self.root, selectmode="extended")
        self.tree.pack(fill="both", expand=True, padx=15, pady=15)

        self.load_treeview()

    def clear_entries(self):
        for entry in self.form_entries.values():
            entry.delete(0, tk.END)


    def build_form(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()
        self.form_entries.clear()

        fields = ["First Name", "Last Name", "Grade"] if self.current_view == "students" else ["First Name", "Last Name", "Subject"]

        for idx, label in enumerate(fields):
            ttk.Label(self.form_frame, text=label).grid(row=idx, column=0, sticky='e', padx=5, pady=5)
            entry = ttk.Entry(self.form_frame, width=35)
            entry.grid(row=idx, column=1, padx=5, pady=5)
            self.form_entries[label.lower().replace(" ", "_")] = entry

    def load_students_view(self):
        self.current_view = "students"
        self.build_form()
        self.load_treeview()

    def load_teachers_view(self):
        self.current_view = "teachers"
        self.build_form()
        self.load_treeview()

    def switch_view(self, view):
        self.current_view = view
        self.build_form()
        self.load_treeview()



    def load_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.tree["columns"] = ("id", "first_name", "last_name", "third_field")
        self.tree.heading("#0", text="", anchor="w")
        self.tree.column("#0", width=0, stretch=tk.NO)

        self.tree.heading("id", text="ID")
        self.tree.column("id", width=50)

        self.tree.heading("first_name", text="First Name")
        self.tree.column("first_name", width=150)

        self.tree.heading("last_name", text="Last Name")
        self.tree.column("last_name", width=150)

        third_col = "Grade" if self.current_view == "students" else "Subject"
        self.tree.heading("third_field", text=third_col)
        self.tree.column("third_field", width=150)

        conn = get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT id, first_name, last_name, {third_col.lower()} FROM {self.current_view}")
                for row in cur.fetchall():
                    self.tree.insert("", tk.END, values=row)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{e}")
        finally:
            conn.close()
        
        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

    def insert_record(self):
        data = {k: v.get().strip() for k, v in self.form_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        conn = get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                col3 = "grade" if self.current_view == "students" else "subject"
                cur.execute(
                    f"""
                    INSERT INTO {self.current_view} (first_name, last_name, {col3})
                    VALUES (%s, %s, %s)
                    """,
                    (data["first_name"], data["last_name"], data[col3])
                )
            conn.commit()
            messagebox.showinfo("Success", "Record inserted successfully.")
            self.load_treeview()
            self.clear_entries()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Insert Failed", str(e))
        finally:
            conn.close()

    
    def update_record(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No selection", "Select a record to update.")
            return

        values = self.tree.item(selected, "values")
        record_id = values[0]
        data = {k: v.get().strip() for k, v in self.form_entries.items()}

        if not all(data.values()):
            messagebox.showwarning("Input Error", "Please fill out all fields.")
            return

        conn = get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                col3 = "grade" if self.current_view == "students" else "subject"
                cur.execute(
                    f"""
                    UPDATE {self.current_view}
                    SET first_name=%s, last_name=%s, {col3}=%s
                    WHERE id=%s
                    """,
                    (data["first_name"], data["last_name"], data[col3], record_id)
             )
            conn.commit()
            messagebox.showinfo("Updated", "Record updated successfully.")
            self.load_treeview()
            self.clear_entries()
        except Exception as e:
         conn.rollback()
         messagebox.showerror("Update Failed", str(e))
        finally:
         conn.close()



    def delete_record(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("No selection", "Select one or more records to delete.")
            return

        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete selected record(s)?")
        if not confirm:
            return

        col3 = "grade" if self.current_view == "students" else "subject"
        table = self.current_view
        backup = f"{table}_backup"

        conn = get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
             for item in selected_items:
                 values = self.tree.item(item, "values")
                 record_id = values[0]
                 cur.execute(f"""
                     INSERT INTO {backup} (first_name, last_name, {col3})
                     SELECT first_name, last_name, {col3} FROM {table} WHERE id = %s
                 """, (record_id,))
                 cur.execute(f"DELETE FROM {table} WHERE id = %s", (record_id,))
            conn.commit()
            messagebox.showinfo("Deleted", "Selected record(s) deleted.")
            self.load_treeview()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Delete Failed", str(e))
        finally:
            conn.close()

    def undo_delete(self):
        col3 = "grade" if self.current_view == "students" else "subject"
        table = self.current_view
        backup = f"{table}_backup"

        conn = get_connection()
        if not conn:
            return
        try:
            with conn.cursor() as cur:
                # Get the most recent deleted_at timestamp
                cur.execute(f"SELECT MAX(deleted_at) FROM {backup}")
                latest_time = cur.fetchone()[0]

                if not latest_time:
                    messagebox.showinfo("Undo", "No backup records to restore.")
                    return

                # Fetch rows to restore
                cur.execute(f"""
                    SELECT id, first_name, last_name, {col3}
                    FROM {backup}
                    WHERE deleted_at = %s
                """, (latest_time,))
                rows = cur.fetchall()

                for row in rows:
                    record_id, first_name, last_name, third = row
                    # Insert with original ID
                    cur.execute(
                        f"""
                        INSERT INTO {table} (id, first_name, last_name, {col3})
                        VALUES (%s, %s, %s, %s)
                        """, (record_id, first_name, last_name, third)
                    )
                    # Remove from backup
                    cur.execute(f"DELETE FROM {backup} WHERE id = %s", (record_id,))

            conn.commit()
            messagebox.showinfo("Undo", f"Restored {len(rows)} record(s) with original ID(s).")
            self.load_treeview()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Undo Failed", str(e))
        finally:
            conn.close()


    def on_row_select(self, event):
        selected = self.tree.focus()
        if not selected:
            return
        values = self.tree.item(selected, "values")
        keys = list(self.form_entries.keys())
        for i in range(3):
            self.form_entries[keys[i]].delete(0, tk.END)
            self.form_entries[keys[i]].insert(0, values[i + 1])  # skip id

# Start App
if __name__ == "__main__":
    root = tk.Tk()
    app = University(root)
    root.mainloop()
