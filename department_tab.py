import tkinter as tk
from tkinter import ttk

class DepartmentTab:
    def __init__(self, parent, cursor, conn):
        self.tab = ttk.Frame(parent)
        self.cursor = cursor
        self.conn = conn

        self.label_department_name = ttk.Label(self.tab, text="Department Name:")

        # Entry widgets
        self.entry_department_name = ttk.Entry(self.tab)

        # Dropdown for selecting CourseID
        self.label_course_id = ttk.Label(self.tab, text="Course ID:")
        self.combo_course_id = ttk.Combobox(self.tab, state="readonly")

        # Buttons
        self.button_add_department = ttk.Button(self.tab, text="Add Department", command=self.add_department)
        self.button_update_department = ttk.Button(self.tab, text="Update Department", command=self.update_department)
        self.button_delete_department = ttk.Button(self.tab, text="Delete Department", command=self.delete_department)

        columns = ("Department ID", "Department Name", "Course ID")
        # Treeview for displaying department data
        self.tree_departments = ttk.Treeview(self.tab, columns=columns, show="headings")
        self.tree_departments.heading("Department ID", text="Department ID")
        self.tree_departments.heading("Department Name", text="Department Name")
        self.tree_departments.heading("Course ID", text="Course ID")

        self.scrollbar_departments = ttk.Scrollbar(self.tab, orient="vertical", command=self.tree_departments.yview)
        self.tree_departments.configure(yscrollcommand=self.scrollbar_departments.set)

        # Grid layout for Treeview and Scrollbar
        self.tree_departments.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky="nsew")
        self.scrollbar_departments.grid(row=0, column=3, rowspan=7, pady=10, sticky="ns")

        # Grid layout
        self.label_department_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_course_id.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.entry_department_name.grid(row=0, column=1, padx=10, pady=5)
        self.combo_course_id.grid(row=1, column=1, padx=10, pady=5)

        self.button_add_department.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_update_department.grid(row=4, column=0, columnspan=2, pady=10)
        self.button_delete_department.grid(row=6, column=0, columnspan=2, pady=10)

        # Populate treeview and combo box initially
        self.query_departments()
        self.populate_course_dropdown()

    def add_department(self):
        department_name = self.entry_department_name.get()
        course_id = self.combo_course_id.get()

        if department_name and course_id:
            # Check if the entered CourseID exists in the Courses table
            if self.course_exists(course_id):
                # Fetch the last inserted DepartmentID
                self.cursor.execute("SELECT MAX(DepartmentID) FROM Departments;")
                last_department_id = self.cursor.fetchone()[0]

                # Increment the last DepartmentID by 1
                new_department_id = last_department_id + 1 if last_department_id is not None else 1

                query = "INSERT INTO Departments (DepartmentID, DepartmentName, CourseID) VALUES (%s, %s, %s);"
                self.cursor.execute(query, (new_department_id, department_name, course_id))
                self.conn.commit()

                self.clear_department_entries()
                self.query_departments()
                print(f"Department added with ID: {new_department_id}")
            else:
                print("Error: Course with the specified ID does not exist.")
        else:
            print("Please fill in all fields.")


    def update_department(self):
        selected_item = self.tree_departments.selection()
        if selected_item:
            department_id = self.tree_departments.item(selected_item, "values")[0]
            department_name = self.entry_department_name.get()
            course_id = self.combo_course_id.get()

            if department_name and course_id:
                # Check if the entered CourseID exists in the Courses table
                if self.course_exists(course_id):
                    query = "UPDATE Departments SET DepartmentName=%s, CourseID=%s WHERE DepartmentID=%s;"
                    self.cursor.execute(query, (department_name, course_id, department_id))
                    self.conn.commit()

                    self.clear_department_entries()
                    self.query_departments()
                    print(f"Department with ID {department_id} updated.")
                else:
                    print("Error: Course with the specified ID does not exist.")
            else:
                print("Please fill in all fields.")
        else:
            print("Please select a department to update.")

    def query_departments(self):
        # Clear existing data in the treeview
        for item in self.tree_departments.get_children():
            self.tree_departments.delete(item)

        query = "SELECT * FROM Departments ORDER BY DepartmentID;"
        self.cursor.execute(query)
        departments = self.cursor.fetchall()

        for department in departments:
            self.tree_departments.insert("", "end", values=department)

    def delete_department(self):
        selected_item = self.tree_departments.selection()
        if selected_item:
            department_id = self.tree_departments.item(selected_item, "values")[0]

            # Now you can safely delete the department
            query = "DELETE FROM Departments WHERE DepartmentID=%s;"
            self.cursor.execute(query, (department_id,))
            self.conn.commit()

            self.clear_department_entries()
            self.query_departments()
            print(f"Department with ID {department_id} deleted.")
        else:
            print("Please select a department to delete.")

    def clear_department_entries(self):
        self.entry_department_name.delete(0, "end")
        self.combo_course_id.set("")

    def populate_course_dropdown(self):
        # Fetch the existing Course IDs from the Courses table
        query = "SELECT CourseID FROM Courses;"
        self.cursor.execute(query)
        course_ids = self.cursor.fetchall()

        # Populate the combo box with Course IDs
        self.combo_course_id["values"] = course_ids

    def course_exists(self, course_id):
        # Check if the entered CourseID exists in the Courses table
        query = "SELECT * FROM Courses WHERE CourseID=%s;"
        self.cursor.execute(query, (course_id,))
        return bool(self.cursor.fetchone())
