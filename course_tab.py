import tkinter as tk
from tkinter import ttk

class CourseTab:
    def __init__(self, parent, cursor, conn):
        self.tab = ttk.Frame(parent)
        self.cursor = cursor
        self.conn = conn

        self.label_course_name = ttk.Label(self.tab, text="Course Name:")
        self.label_credits = ttk.Label(self.tab, text="Credits:")

        # Entry widgets
        self.entry_course_name = ttk.Entry(self.tab)
        self.entry_credits = ttk.Entry(self.tab)

        # Buttons
        self.button_add_course = ttk.Button(self.tab, text="Add Course", command=self.add_course)
        self.button_update_course = ttk.Button(self.tab, text="Update Course", command=self.update_course)
        self.button_delete_course = ttk.Button(self.tab, text="Delete Course", command=self.delete_course)

        columns = ("Course ID", "Course Name", "Credits")
        # Treeview for displaying course data
        self.tree_courses = ttk.Treeview(self.tab, columns=columns, show="headings")
        self.tree_courses.heading("Course ID", text="Course ID")
        self.tree_courses.heading("Course Name", text="Course Name")
        self.tree_courses.heading("Credits", text="Credits")

        self.scrollbar_courses = ttk.Scrollbar(self.tab, orient="vertical", command=self.tree_courses.yview)
        self.tree_courses.configure(yscrollcommand=self.scrollbar_courses.set)

        # Grid layout for Treeview and Scrollbar
        self.tree_courses.grid(row=0, column=2, rowspan=7, padx=10, pady=10, sticky="nsew")
        self.scrollbar_courses.grid(row=0, column=3, rowspan=7, pady=10, sticky="ns")

        # Grid layout
        self.label_course_name.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.label_credits.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.entry_course_name.grid(row=0, column=1, padx=10, pady=5)
        self.entry_credits.grid(row=1, column=1, padx=10, pady=5)

        self.button_add_course.grid(row=3, column=0, columnspan=2, pady=10)
        self.button_update_course.grid(row=4, column=0, columnspan=2, pady=10)
        self.button_delete_course.grid(row=6, column=0, columnspan=2, pady=10)

        self.tree_courses.grid(row=0, column=2, rowspan=7, padx=10, pady=10)

        # Populate treeview initially
        self.query_courses()

    def add_course(self):
        course_name = self.entry_course_name.get()
        credits = self.entry_credits.get()

        if course_name and credits:
            # Fetch the last inserted CourseID
            self.cursor.execute("SELECT MAX(CourseID) FROM Courses;")
            last_course_id = self.cursor.fetchone()[0]

            # Increment the last CourseID by 1
            new_course_id = last_course_id + 1 if last_course_id is not None else 1

            query = "INSERT INTO Courses (CourseID, CourseName, Credits) VALUES (%s, %s, %s);"
            self.cursor.execute(query, (new_course_id, course_name, credits))
            self.conn.commit()

            self.clear_course_entries()
            self.query_courses()
            print(f"Course added with ID: {new_course_id}")
        else:
            print("Please fill in all fields.")

    def update_course(self):
        selected_item = self.tree_courses.selection()
        if selected_item:
            course_id = self.tree_courses.item(selected_item, "values")[0]
            course_name = self.entry_course_name.get()
            credits = self.entry_credits.get()

            if course_name and credits:
                query = "UPDATE Courses SET CourseName=%s, Credits=%s WHERE CourseID=%s;"
                self.cursor.execute(query, (course_name, credits, course_id))
                self.conn.commit()

                self.clear_course_entries()
                self.query_courses()
                print(f"Course with ID {course_id} updated.")
            else:
                print("Please fill in all fields.")
        else:
            print("Please select a course to update.")

    def query_courses(self):
        # Clear existing data in the treeview
        for item in self.tree_courses.get_children():
            self.tree_courses.delete(item)

        query = "SELECT * FROM Courses ORDER BY CourseID;"
        self.cursor.execute(query)
        courses = self.cursor.fetchall()

        for course in courses:
            self.tree_courses.insert("", "end", values=course)

    def delete_course(self):
        selected_item = self.tree_courses.selection()
        if selected_item:
            course_id = self.tree_courses.item(selected_item, "values")[0]

            # Check for references in the enrollments table
            enrollment_query = "SELECT * FROM enrollments WHERE courseid = %s;"
            self.cursor.execute(enrollment_query, (course_id,))
            enrollments = self.cursor.fetchall()

            if enrollments:
                # If there are references, ask for confirmation to delete related enrollments
                delete_enrollment_query = "DELETE FROM enrollments WHERE courseid=%s;"
                self.cursor.execute(delete_enrollment_query, (course_id,))
                self.conn.commit()

            # Check for references in the teaches table
            grades_querry = "SELECT * FROM grades WHERE courseid = %s;"
            self.cursor.execute(grades_querry, (course_id,))
            grades_entries = self.cursor.fetchall()

            if grades_entries:
                # If there are references in teaches, delete them first
                delete_grades_query = "DELETE FROM grades WHERE courseid=%s;"
                self.cursor.execute(delete_grades_query, (course_id,))
                self.conn.commit()

            departments_querry = "SELECT * FROM departments WHERE courseid = %s;"
            self.cursor.execute(departments_querry, (course_id,))
            departmetns_entries = self.cursor.fetchall()

            if departmetns_entries:
                # If there are references in teaches, delete them first
                delete_departments_query = "DELETE FROM departments WHERE courseid=%s;"
                self.cursor.execute(delete_departments_query, (course_id,))
                self.conn.commit()

            # Now you can safely delete the course
            query = "DELETE FROM Courses WHERE CourseID=%s;"
            self.cursor.execute(query, (course_id,))
            self.conn.commit()

            self.clear_course_entries()
            self.query_courses()
            print(f"Course with ID {course_id} deleted.")
        else:
            print("Please select a course to delete.")


    def clear_course_entries(self):
        self.entry_course_name.delete(0, "end")
        self.entry_credits.delete(0, "end")
