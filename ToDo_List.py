import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3
import csv

# Database Module
class Database:
    def __init__(self, db_name="tasks.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Pending'
        )''')
        self.connection.commit()

    def add_task(self, title, description):
        self.cursor.execute("INSERT INTO tasks (title, description) VALUES (?, ?)", (title, description))
        self.connection.commit()

    def get_tasks(self):
        self.cursor.execute("SELECT * FROM tasks")
        return self.cursor.fetchall()

    def update_task(self, task_id, title, description, status):
        self.cursor.execute("""
            UPDATE tasks SET title = ?, description = ?, status = ? WHERE id = ?
        """, (title, description, status, task_id))
        self.connection.commit()

    def delete_task(self, task_id):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.connection.commit()

    def export_to_csv(self, file_name):
        tasks = self.get_tasks()
        with open(file_name, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["ID", "Title", "Description", "Status"])
            writer.writerows(tasks)

    def __del__(self):
        self.connection.close()

# GUI Module
class ToDoApp:
    def __init__(self, root):
        self.db = Database()
        self.root = root
        self.root.title("To-Do List Application")
        self.setup_ui()
        self.setup_button_hover_effects()

    def setup_ui(self):
        # Task Input Section
        self.title_label = tk.Label(self.root, text="Task Title:")
        self.title_label.pack(pady=5)
        self.title_entry = tk.Entry(self.root, width=40)
        self.title_entry.pack(pady=5)

        self.desc_label = tk.Label(self.root, text="Task Description:")
        self.desc_label.pack(pady=5)
        self.desc_entry = tk.Entry(self.root, width=40)
        self.desc_entry.pack(pady=5)

        # Add Task Button - Green theme
        self.add_button = tk.Button(self.root, 
            text="Add Task",
            command=self.add_task,
            bg="#4CAF50",  # Green background
            fg="white",    # White text
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            padx=20)
        self.add_button.pack(pady=10)

        # Task List Section
        self.task_listbox = tk.Listbox(self.root, width=50, height=15)
        self.task_listbox.pack(pady=10)
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)

        # Update Button - Blue theme
        self.update_button = tk.Button(self.root, 
            text="Update Task",
            command=self.update_task,
            bg="#2196F3",  # Blue background
            fg="white",    # White text
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            state=tk.DISABLED,
            padx=20)
        self.update_button.pack(pady=5)

        # Delete Button - Red theme
        self.delete_button = tk.Button(self.root, 
            text="Delete Task",
            command=self.delete_task,
            bg="#f44336",  # Red background
            fg="white",    # White text
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            state=tk.DISABLED,
            padx=20)
        self.delete_button.pack(pady=5)

        # Export Button - Orange theme
        self.export_button = tk.Button(self.root, 
            text="Export to CSV",
            command=self.export_tasks,
            bg="#FF9800",  # Orange background
            fg="white",    # White text
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
            padx=20)
        self.export_button.pack(pady=5)

        self.load_tasks()

    def setup_button_hover_effects(self):
        # Add hover effects for all buttons
        buttons = [
            (self.add_button, "#45a049", "#4CAF50"),    # Green
            (self.update_button, "#1976D2", "#2196F3"),  # Blue
            (self.delete_button, "#d32f2f", "#f44336"),  # Red
            (self.export_button, "#F57C00", "#FF9800"),  # Orange
        ]
        
        for button, hover_color, default_color in buttons:
            button.bind("<Enter>", lambda e, btn=button, color=hover_color: 
                btn.configure(bg=color))
            button.bind("<Leave>", lambda e, btn=button, color=default_color: 
                btn.configure(bg=color))

    def add_task(self):
        title = self.title_entry.get().strip()
        description = self.desc_entry.get().strip()
        if not title:
            messagebox.showerror("Error", "Task title cannot be empty!")
            return
        self.db.add_task(title, description)
        self.load_tasks()
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

    def load_tasks(self):
        self.task_listbox.delete(0, tk.END)
        tasks = self.db.get_tasks()
        for task in tasks:
            self.task_listbox.insert(tk.END, f"{task[0]}: {task[1]} ({task[3]})")

    def on_task_select(self, event):
        try:
            self.selected_task = self.task_listbox.get(self.task_listbox.curselection())
            self.update_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
        except tk.TclError:
            self.selected_task = None

    def update_task(self):
        if not self.selected_task:
            return

        task_id = int(self.selected_task.split(":")[0])
        task_details = self.db.get_tasks()
        task = next((t for t in task_details if t[0] == task_id), None)

        if task:
            title = simpledialog.askstring("Update Task", "Enter new title:", initialvalue=task[1])
            description = simpledialog.askstring("Update Task", "Enter new description:", initialvalue=task[2])
            status = simpledialog.askstring("Update Task", "Enter status (Pending/Completed):", initialvalue=task[3])

            if title and status in ("Pending", "Completed"):
                self.db.update_task(task_id, title.strip(), description.strip() if description else "", status.strip())
                self.load_tasks()
            else:
                messagebox.showerror("Error", "Invalid inputs for task update.")

    def delete_task(self):
        if not self.selected_task:
            return
        task_id = int(self.selected_task.split(":")[0])
        self.db.delete_task(task_id)
        self.load_tasks()
        self.update_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)

    def export_tasks(self):
        file_name = "tasks_export.csv"
        self.db.export_to_csv(file_name)
        messagebox.showinfo("Export Successful", f"Tasks exported to {file_name}")

# Run the Application
if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()