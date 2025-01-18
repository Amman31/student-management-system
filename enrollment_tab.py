import tkinter as tk
from tkinter import ttk

class EnrollmentTab:
    def __init__(self, parent, cursor, conn):
        self.tab = ttk.Frame(parent)
        self.cursor = cursor
        self.conn = conn

        self.label_student_id = ttk.Label(self.tab, text="Student ID:")
        self.label_course_id = ttk.Label(self.tab, text="Course ID:")

        # Dropdown menus
        self.student_options = self.get_student_options()
        self.course_options = self.get_course_options()

        self.student_combobox = ttk.Combobox(self.tab, values=self.student_options, state="readonly")
        self.course_combobox = ttk.Combobox(self.tab, values=self.course_options, state="readonly")

        # Buttons
        self.button_enroll_student = ttk.Button(self.tab, text="Enroll Student", command=self.enroll_student)
        self.button_delete_enrollment = ttk.Button(self.tab, text="Delete Enrollment", command=self.delete_enrollment)

        columns = ("Enrollment ID", "Student ID", "Course ID")
        # Treeview for displaying enrollment data
        self.tree_enrollments = ttk.Treeview(self.tab, columns=columns, show="headings")
        self.tree_enrollments.heading("Enrollment ID", text="Enrollment ID")
        self.tree_enrollments.heading("Student ID", text="Student ID")
        self.tree_enrollments.heading("Course ID", text="Course ID")

        self.scrollbar_enrollments = ttk.Scrollbar(self.tab, orient="vertical", command=self.tree_enrollments.yview)
        self.tree_enrollments.configure(yscrollcommand=self.scrollbar_enrollments.set)

        # Grid layout for Treeview and Scrollbar
        self.tree_enrollments.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky="nsew")
        self.scrollbar_enrollments.grid(row=0, column=3, rowspan=7, pady=10, sticky="ns")

        # Grid layout
        self.label_student_id.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_course_id.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.student_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.course_combobox.grid(row=1, column=1, padx=10, pady=5)

        self.button_enroll_student.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_delete_enrollment.grid(row=4, column=0, columnspan=2, pady=10)

        # Populate treeview initially
        self.query_enrollments()

    def enroll_student(self):
        student_id = self.student_combobox.get()
        course_id = self.course_combobox.get()

        if student_id and course_id:
            # Check if the entered StudentID and CourseID exist in their respective tables
            if self.student_exists(student_id) and self.course_exists(course_id):
                # Get the maximum existing EnrollmentID
                self.cursor.execute("SELECT MAX(EnrollmentID) FROM Enrollments;")
                last_enrollment_id = self.cursor.fetchone()[0]

                # Increment the last EnrollmentID by 1
                new_enrollment_id = last_enrollment_id + 1 if last_enrollment_id is not None else 1

                # Insert the new enrollment with the generated EnrollmentID
                query = "INSERT INTO Enrollments (EnrollmentID, StudentID, CourseID) VALUES (%s, %s, %s);"
                self.cursor.execute(query, (new_enrollment_id, student_id, course_id))
                self.conn.commit()

                self.clear_enrollment_entries()
                self.query_enrollments()
                print(f"Student enrolled with Enrollment ID: {new_enrollment_id}")
            else:
                print("Error: Student or Course with the specified ID does not exist.")
        else:
            print("Please fill in all fields.")


    def delete_enrollment(self):
        selected_item = self.tree_enrollments.selection()
        if selected_item:
            enrollment_id = self.tree_enrollments.item(selected_item, "values")[0]

            # Now you can safely delete the enrollment
            query = "DELETE FROM Enrollments WHERE EnrollmentID=%s;"
            self.cursor.execute(query, (enrollment_id,))
            self.conn.commit()

            self.clear_enrollment_entries()
            self.query_enrollments()
            print(f"Enrollment with ID {enrollment_id} deleted.")
        else:
            print("Please select an enrollment to delete.")

    def query_enrollments(self):
        # Clear existing data in the treeview
        for item in self.tree_enrollments.get_children():
            self.tree_enrollments.delete(item)

        query = "SELECT * FROM Enrollments ORDER BY EnrollmentID;"
        self.cursor.execute(query)
        enrollments = self.cursor.fetchall()

        for enrollment in enrollments:
            self.tree_enrollments.insert("", "end", values=enrollment)

    def clear_enrollment_entries(self):
        self.student_combobox.set("")  # Clear student combobox
        self.course_combobox.set("")

    def student_exists(self, student_id):
        # Check if the entered StudentID exists in the Students table
        query = "SELECT * FROM Students WHERE StudentID=%s;"
        self.cursor.execute(query, (student_id,))
        return bool(self.cursor.fetchone())

    def course_exists(self, course_id):
        # Check if the entered CourseID exists in the Courses table
        query = "SELECT * FROM Courses WHERE CourseID=%s;"
        self.cursor.execute(query, (course_id,))
        return bool(self.cursor.fetchone())


    def get_student_options(self):
        # Retrieve the list of student IDs from the Students table
        query = "SELECT StudentID FROM Students;"
        self.cursor.execute(query)
        students = self.cursor.fetchall()
        return [student[0] for student in students]

    def get_course_options(self):
        # Retrieve the list of course IDs from the Courses table
        query = "SELECT CourseID FROM Courses;"
        self.cursor.execute(query)
        courses = self.cursor.fetchall()
        return [course[0] for course in courses]