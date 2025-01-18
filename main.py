import tkinter as tk
from tkinter import ttk, simpledialog
import psycopg2
from student_tab import StudentTab
from course_tab import CourseTab
from department_tab import DepartmentTab
from enrollment_tab import EnrollmentTab
from grade_tab import GradeTab

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System")

        # Get database, user, and password from user input
        database, user, password = self.get_database_credentials()

        # Connect to PostgreSQL database
        conn = psycopg2.connect(database=database, user=user, password=password)
        cursor = conn.cursor()

        # Create tabs
        self.tabControl = ttk.Notebook(root)

        # Student tab
        student_tab = StudentTab(self.tabControl, cursor, conn)
        self.tabControl.add(student_tab.tab, text="Students")

        # Course tab
        course_tab = CourseTab(self.tabControl, cursor, conn)
        self.tabControl.add(course_tab.tab, text="Courses")

        department_tab = DepartmentTab(self.tabControl, cursor, conn)
        self.tabControl.add(department_tab.tab, text="Departments")

        enrollment_tab = EnrollmentTab(self.tabControl, cursor, conn)
        self.tabControl.add(enrollment_tab.tab, text="Enrollments")

        grade_tab = GradeTab(self.tabControl, cursor, conn)
        self.tabControl.add(grade_tab.tab, text="Grades")

        # Pack the tab control
        self.tabControl.pack(expand=1, fill="both")

    def get_database_credentials(self):
        # Prompt the user for database, user, and password
        database = simpledialog.askstring("Database", "Enter database name:")
        user = simpledialog.askstring("User", "Enter username:")
        password = simpledialog.askstring("Password", "Enter password:", show="*")
        return database, user, password

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('1200x720+130+50')
    app = MainApplication(root)
    root.mainloop()
