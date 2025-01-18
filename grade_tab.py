import tkinter as tk
from tkinter import ttk

class GradeTab:
    def __init__(self, parent, cursor, conn):
        self.tab = ttk.Frame(parent)
        self.cursor = cursor
        self.conn = conn

        self.label_student_id = ttk.Label(self.tab, text="Student ID:")
        self.label_course_id = ttk.Label(self.tab, text="Course ID:")
        self.label_grade = ttk.Label(self.tab, text="Grade:")

        # Dropdown menus
        self.student_options = self.get_student_options()
        self.course_options = self.get_course_options()
        self.grade_options = [0, 1, 2, 3, 4, 5]

        self.student_combobox = ttk.Combobox(self.tab, values=self.student_options, state="readonly")
        self.course_combobox = ttk.Combobox(self.tab, values=self.course_options, state="readonly")
        self.grade_combobox = ttk.Combobox(self.tab, values=self.grade_options, state="readonly")

        # Buttons
        self.button_assign_grade = ttk.Button(self.tab, text="Assign Grade", command=self.assign_grade)
        self.button_delete_grade = ttk.Button(self.tab, text="Delete Grade", command=self.delete_grade)

        columns = ("Grade ID", "Student ID", "Course ID", "Grade")
        # Treeview for displaying grade data
        self.tree_grades = ttk.Treeview(self.tab, columns=columns, show="headings")
        self.tree_grades.heading("Grade ID", text="Grade ID")
        self.tree_grades.heading("Student ID", text="Student ID")
        self.tree_grades.heading("Course ID", text="Course ID")
        self.tree_grades.heading("Grade", text="Grade")

        self.scrollbar_grades = ttk.Scrollbar(self.tab, orient="vertical", command=self.tree_grades.yview)
        self.tree_grades.configure(yscrollcommand=self.scrollbar_grades.set)

        # Grid layout for Treeview and Scrollbar
        self.tree_grades.grid(row=0, column=4, rowspan=7, padx=10, pady=10, sticky="nsew")
        self.scrollbar_grades.grid(row=0, column=5, rowspan=7, pady=10, sticky="ns")

        # Grid layout
        self.label_student_id.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_course_id.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.label_grade.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.student_combobox.grid(row=0, column=1, padx=10, pady=5)
        self.course_combobox.grid(row=1, column=1, padx=10, pady=5)
        self.grade_combobox.grid(row=2, column=1, padx=10, pady=5)

        self.button_assign_grade.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_delete_grade.grid(row=4, column=0, columnspan=2, pady=10)

        # Populate treeview initially
        self.query_grades()

    def assign_grade(self):
        student_id = self.student_combobox.get()
        course_id = self.course_combobox.get()
        grade = self.grade_combobox.get()

        if student_id and course_id and grade:
            # Check if the entered StudentID and CourseID exist in their respective tables
            if self.student_exists(student_id) and self.course_exists(course_id):
                # Get the maximum existing GradeID
                self.cursor.execute("SELECT MAX(GradeID) FROM Grades;")
                last_grade_id = self.cursor.fetchone()[0]

                # Increment the last GradeID by 1
                new_grade_id = last_grade_id + 1 if last_grade_id is not None else 1

                # Insert the new grade with the generated GradeID
                query = "INSERT INTO Grades (GradeID, StudentID, CourseID, Grade) VALUES (%s, %s, %s, %s);"
                self.cursor.execute(query, (new_grade_id, student_id, course_id, grade))
                self.conn.commit()

                self.clear_grade_entries()
                self.query_grades()
                print(f"Grade assigned with Grade ID: {new_grade_id}")
            else:
                print("Error: Student or Course with the specified ID does not exist.")
        else:
            print("Please fill in all fields.")

    def delete_grade(self):
        selected_item = self.tree_grades.selection()
        if selected_item:
            grade_id = self.tree_grades.item(selected_item, "values")[0]

            # Now you can safely delete the grade
            query = "DELETE FROM Grades WHERE GradeID=%s;"
            self.cursor.execute(query, (grade_id,))
            self.conn.commit()

            self.clear_grade_entries()
            self.query_grades()
            print(f"Grade with ID {grade_id} deleted.")
        else:
            print("Please select a grade to delete.")

    def query_grades(self):
        # Clear existing data in the treeview
        for item in self.tree_grades.get_children():
            self.tree_grades.delete(item)

        query = "SELECT * FROM Grades ORDER BY GradeID;"
        self.cursor.execute(query)
        grades = self.cursor.fetchall()

        for grade in grades:
            self.tree_grades.insert("", "end", values=grade)

    def clear_grade_entries(self):
        self.student_combobox.set("")  # Clear student combobox
        self.course_combobox.set("")
        self.grade_combobox.set("")

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