import tkinter as tk
from tkinter import ttk

class StudentTab:
    def __init__(self, parent, cursor, conn):
        self.tab = ttk.Frame(parent)
        self.cursor = cursor
        self.conn = conn

        self.label_firstname = ttk.Label(self.tab, text="First Name:")
        self.label_lastname = ttk.Label(self.tab, text="Last Name:")
        self.label_email = ttk.Label(self.tab, text="Email:")

        # Entry widgets
        self.entry_firstname = ttk.Entry(self.tab)
        self.entry_lastname = ttk.Entry(self.tab)
        self.entry_email = ttk.Entry(self.tab)

        # Buttons
        self.button_add = ttk.Button(self.tab, text="Add Student", command=self.add_student)
        self.button_update = ttk.Button(self.tab, text="Update Student", command=self.update_student)
        self.button_delete = ttk.Button(self.tab, text="Delete Student", command=self.delete_student)

        columns=("Student ID", "First Name", "Last Name", "Email")
        # Treeview for displaying student data
        self.tree = ttk.Treeview(self.tab, columns=columns, show="headings")
        self.tree.heading("Student ID", text="Student ID")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Email", text="Email")

        self.scrollbar = ttk.Scrollbar(self.tab, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)

        # Grid layout for Treeview and Scrollbar
        self.tree.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky="nsew")
        self.scrollbar.grid(row=0, column=3, rowspan=7, pady=10, sticky="ns")


        # Grid layout
        self.label_firstname.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_lastname.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.label_email.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.entry_firstname.grid(row=0, column=1, padx=10, pady=5)
        self.entry_lastname.grid(row=1, column=1, padx=10, pady=5)
        self.entry_email.grid(row=2, column=1, padx=10, pady=5)

        self.button_add.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_update.grid(row=4, column=0, columnspan=2, pady=10)
        self.button_delete.grid(row=6, column=0, columnspan=2, pady=10)

        self.tree.grid(row=0, column=2, rowspan=7, padx=10, pady=10)

        # Populate treeview initially
        self.query_students()

    def add_student(self):
        first_name = self.entry_firstname.get()
        last_name = self.entry_lastname.get()
        email = self.entry_email.get()

        if first_name and last_name and email:
            # Fetch the last inserted StudentID
            self.cursor.execute("SELECT MAX(StudentID) FROM Students;")
            last_student_id = self.cursor.fetchone()[0]

            # Increment the last StudentID by 1
            new_student_id = last_student_id + 1 if last_student_id is not None else 1

            query = "INSERT INTO Students (StudentID, FirstName, LastName, Email) VALUES (%s, %s, %s, %s);"
            self.cursor.execute(query, (new_student_id, first_name, last_name, email))
            self.conn.commit()

            self.clear_entries()
            self.query_students()
            print(f"Student added with ID: {new_student_id}")
        else:
            print("Please fill in all fields.")


    def update_student(self):
        selected_item = self.tree.selection()
        if selected_item:
            student_id = self.tree.item(selected_item, "values")[0]
            first_name = self.entry_firstname.get()
            last_name = self.entry_lastname.get()
            email = self.entry_email.get()

            if first_name and last_name and email:
                query = "UPDATE Students SET FirstName=%s, LastName=%s, Email=%s WHERE StudentID=%s;"
                self.cursor.execute(query, (first_name, last_name, email, student_id))
                self.conn.commit()

                self.clear_entries()
                self.query_students()
                print(f"Student with ID {student_id} updated.")
            else:
                print("Please fill in all fields.")
        else:
            print("Please select a student to update.")

    def query_students(self):
        # Clear existing data in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = "SELECT * FROM Students ORDER BY StudentID;"
        self.cursor.execute(query)
        students = self.cursor.fetchall()

        for student in students:
            self.tree.insert("", "end", values=student)

    def delete_student(self):
        selected_item = self.tree.selection()
        if selected_item:
            student_id = self.tree.item(selected_item, "values")[0]

            enrollment_query = "SELECT * FROM enrollments WHERE studentid = %s;"
            self.cursor.execute(enrollment_query, (student_id,))
            enrollments = self.cursor.fetchall()

            if enrollments:
                # If there are references, ask for confirmation to delete related enrollments
                delete_enrollment_query = "DELETE FROM enrollments WHERE studentid=%s;"
                self.cursor.execute(delete_enrollment_query, (student_id,))
                self.conn.commit()

            # Check for references in the teaches table
            grades_querry = "SELECT * FROM grades WHERE studentid = %s;"
            self.cursor.execute(grades_querry, (student_id,))
            grades_entries = self.cursor.fetchall()

            if grades_entries:
                # If there are references in teaches, delete them first
                delete_grades_query = "DELETE FROM grades WHERE studentid=%s;"
                self.cursor.execute(delete_grades_query, (student_id,))
                self.conn.commit()

            query = "DELETE FROM Students WHERE StudentID=%s;"
            self.cursor.execute(query, (student_id,))
            self.conn.commit()

            self.clear_entries()
            self.query_students()
            print(f"Student with ID {student_id} deleted.")
        else:
            print("Please select a student to delete.")

    def clear_entries(self):
        self.entry_firstname.delete(0, "end")
        self.entry_lastname.delete(0, "end")
        self.entry_email.delete(0, "end")
