# School Management System with Classes
import psycopg2
from psycopg2 import errors

class DatabaseConnection:
    def __init__(self, host, database, user, password, port):
        try:
            self.conn = psycopg2.connect(
                host='localhost',           # PostgreSQL host
                database='regftu',           # PostgreSQL database name
                user='postgres',            # PostgreSQL username
                password='admin',           # PostgreSQL password
                port='5432'
            )
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Database connection error: {e}")
            exit()

    def close(self):
        self.cursor.close()
        self.conn.close()
        print("Database connection closed.")

class User:
    def __init__(self, db):
        self.db = db

    def register(self):
        while True:
            try:
                name = input("Enter your name: ")
                username = input("Create a username: ")
                password = input("Create a password: ")

                while True:
                    role = input("Enter your role (Teacher/Student): ").capitalize()
                    if role in ['Teacher', 'Student']:
                        break
                    else:
                        print("Invalid role. Please enter 'Teacher' or 'Student'.")

                self.db.cursor.execute('''
                    INSERT INTO Users (name, username, password, role) 
                    VALUES (%s, %s, %s, %s)
                ''', (name, username, password, role))
                self.db.conn.commit()
                print(f"{role} registered successfully.")
                break
            except errors.UniqueViolation:
                self.db.conn.rollback()
                print("Username already exists. Please choose another.")
            except Exception as e:
                print(f"Error: {e}")
                if input("Do you want to try again? (y/n): ").lower() != 'y':
                    break

    def login(self):
        while True:
            try:
                username = input("Username: ")
                password = input("Password: ")

                self.db.cursor.execute('''
                    SELECT * FROM Users WHERE username = %s AND password = %s
                ''', (username, password))
                user = self.db.cursor.fetchone()

                if user:
                    print(f"\nWelcome {user[1]}! Logged in as {user[4]}.")
                    if user[4] == 'Teacher':
                        Teacher(self.db, user).menu()
                    elif user[4] == 'Student':
                        Student(self.db, user).menu()
                    break
                else:
                    print("Invalid credentials.")
                    if input("Do you want to try logging in again? (y/n): ").lower() != 'y':
                        break
            except Exception as e:
                print(f"Error: {e}")
                break

class Teacher:
    def __init__(self, db, user):
        self.db = db
        self.user = user

    def menu(self):
        while True:
            print("\n--- Teacher Menu ---")
            print("1. View Subjects and Students")
            print("2. Add Subject")
            print("3. Add/Edit Student Grades")
            print("4. View Teaching Schedule")
            print("5. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.view_subjects_and_students()
            elif choice == '2':
                self.add_subject()
            elif choice == '3':
                self.edit_student_grades()
            elif choice == '4':
                self.view_schedule()
            elif choice == '5':
                print("Logged out.")
                break
            else:
                print("Invalid option. Please try again.")

    def view_subjects_and_students(self):
        self.db.cursor.execute('''
            SELECT id, name, description, schedule FROM Subjects WHERE teacher_id = %s
        ''', (self.user[0],))
        subjects = self.db.cursor.fetchall()

        if not subjects:
            print("No subjects found.")
        else:
            for subj in subjects:
                print(f"\nSubject: {subj[1]}\nDescription: {subj[2]}\nSchedule: {subj[3]}")
                self.db.cursor.execute('''
                    SELECT u.name FROM Enrollments e
                    JOIN Users u ON e.student_id = u.id
                    WHERE e.subject_id = %s
                ''', (subj[0],))
                students = self.db.cursor.fetchall()
                print("Students:")
                for student in students:
                    print(f"- {student[0]}")

    def add_subject(self):
        name = input("Subject Name: ")
        description = input("Subject Description: ")
        schedule = input("Schedule (e.g., Monday 13.00-15.00): ")
        self.db.cursor.execute('''
            INSERT INTO Subjects (name, description, schedule, teacher_id) 
            VALUES (%s, %s, %s, %s)
        ''', (name, description, schedule, self.user[0]))
        self.db.conn.commit()
        print("Subject added successfully.")

    def edit_student_grades(self):
        self.db.cursor.execute('SELECT id, name FROM Subjects WHERE teacher_id = %s', (self.user[0],))
        subjects = self.db.cursor.fetchall()

        if not subjects:
            print("No subjects found.")
            return

        print("Subjects:")
        for subj in subjects:
            print(f"{subj[0]}: {subj[1]}")

        try:
            subject_id = int(input("Enter subject ID to edit grades: "))
            self.db.cursor.execute('''
                SELECT e.id, u.name, e.grade FROM Enrollments e
                JOIN Users u ON e.student_id = u.id
                WHERE e.subject_id = %s
            ''', (subject_id,))
            enrollments = self.db.cursor.fetchall()

            if not enrollments:
                print("No students enrolled in this subject.")
                return

            for enrollment in enrollments:
                print(f"{enrollment[0]}: {enrollment[1]} - Grade: {enrollment[2]}")
                if input("Edit grade? (y/n): ").lower() == 'y':
                    new_grade = float(input("Enter new grade: "))
                    self.db.cursor.execute('UPDATE Enrollments SET grade = %s WHERE id = %s', (new_grade, enrollment[0]))
                    self.db.conn.commit()
                    print("Grade updated.")
        except ValueError:
            print("Invalid subject ID.")

    def view_schedule(self):
        self.db.cursor.execute('''
            SELECT schedule, name FROM Subjects WHERE teacher_id = %s ORDER BY schedule
        ''', (self.user[0],))
        schedule = self.db.cursor.fetchall()

        if not schedule:
            print("No schedule available.")
        else:
            print("\nTeaching Schedule:")
            for sch in schedule:
                print(f"{sch[0]} ({sch[1]})")

class Student:
    def __init__(self, db, user):
        self.db = db
        self.user = user

    def menu(self):
        while True:
            print("\n--- Student Menu ---")
            print("1. View Enrolled Subjects")
            print("2. View Grades")
            print("3. View Class Schedule")
            print("4. Add/Drop Subject")
            print("5. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                self.view_enrolled_subjects()
            elif choice == '2':
                self.view_grades()
            elif choice == '3':
                self.view_class_schedule()
            elif choice == '4':
                self.add_drop_subject()
            elif choice == '5':
                print("Logged out.")
                break
            else:
                print("Invalid option. Please try again.")

    def view_enrolled_subjects(self):
        self.db.cursor.execute('''
            SELECT s.name, s.description, s.schedule 
            FROM Subjects s
            JOIN Enrollments e ON s.id = e.subject_id
            WHERE e.student_id = %s
        ''', (self.user[0],))
        subjects = self.db.cursor.fetchall()

        if subjects:
            print("\n--- Enrolled Subjects ---")
            for idx, subj in enumerate(subjects, 1):
                print(f"{idx}. {subj[0]}\n   Schedule: {subj[2]}\n   Description: {subj[1]}\n")
        else:
            print("No enrolled subjects.")

    def view_grades(self):
        self.db.cursor.execute('''
            SELECT s.name, e.grade 
            FROM Subjects s
            JOIN Enrollments e ON s.id = e.subject_id
            WHERE e.student_id = %s
        ''', (self.user[0],))
        grades = self.db.cursor.fetchall()

        if grades:
            print("\n--- Your Grades ---")
            for subj, grade in grades:
                print(f"{subj}: {grade if grade is not None else 'Not graded yet'}")
        else:
            print("No grades available.")

    def view_class_schedule(self):
        self.db.cursor.execute('''
            SELECT s.schedule, s.name 
            FROM Subjects s
            JOIN Enrollments e ON s.id = e.subject_id
            WHERE e.student_id = %s
            ORDER BY 
                CASE 
                    WHEN s.schedule LIKE 'Sunday%' THEN 1
                    WHEN s.schedule LIKE 'Monday%' THEN 2
                    WHEN s.schedule LIKE 'Tuesday%' THEN 3
                    WHEN s.schedule LIKE 'Wednesday%' THEN 4
                    WHEN s.schedule LIKE 'Thursday%' THEN 5
                    ELSE 6
                END
        ''', (self.user[0],))
        schedule = self.db.cursor.fetchall()

        if schedule:
            print("\n--- Your Class Schedule ---")
            for sch, name in schedule:
                print(f"{sch} ({name})")
        else:
            print("No schedule available.")

    def add_drop_subject(self):
        while True:
            print("\n--- Add/Drop Subject ---")
            print("1. Add Subject")
            print("2. Drop Subject")
            print("3. Back to Student Menu")
            choice = input("Select an option: ")

            if choice == '1':
                self.add_subject()
            elif choice == '2':
                self.drop_subject()
            elif choice == '3':
                break
            else:
                print("Invalid option. Please try again.")

    def add_subject(self):
        self.db.cursor.execute('SELECT id, name FROM Subjects')
        subjects = self.db.cursor.fetchall()

        print("\n--- Available Subjects ---")
        for subj in subjects:
            print(f"{subj[0]}: {subj[1]}")

        try:
            subject_id = int(input("Enter the subject ID to add: "))
            self.db.cursor.execute('''
                SELECT * FROM Enrollments WHERE student_id = %s AND subject_id = %s
            ''', (self.user[0], subject_id))

            if self.db.cursor.fetchone():
                print("You are already enrolled in this subject.")
            else:
                self.db.cursor.execute('''
                    INSERT INTO Enrollments (student_id, subject_id) VALUES (%s, %s)
                ''', (self.user[0], subject_id))
                self.db.conn.commit()
                print("Subject added successfully.")
        except ValueError:
            print("Invalid input. Please enter a valid subject ID.")

    def drop_subject(self):
        self.db.cursor.execute('''
            SELECT s.id, s.name 
            FROM Subjects s
            JOIN Enrollments e ON s.id = e.subject_id
            WHERE e.student_id = %s
        ''', (self.user[0],))
        enrolled_subjects = self.db.cursor.fetchall()

        if enrolled_subjects:
            print("\n--- Enrolled Subjects ---")
            for subj in enrolled_subjects:
                print(f"{subj[0]}: {subj[1]}")

            try:
                subject_id = int(input("Enter the subject ID to drop: "))
                self.db.cursor.execute('''
                    DELETE FROM Enrollments WHERE student_id = %s AND subject_id = %s
                ''', (self.user[0], subject_id))
                self.db.conn.commit()
                print("Subject dropped successfully.")
            except ValueError:
                print("Invalid input. Please enter a valid subject ID.")
        else:
            print("You are not enrolled in any subjects.")

class SchoolManagementSystem:
    def __init__(self):
        self.db = DatabaseConnection(
            host='localhost',
            database='regftu',
            user='postgres',
            password='admin',
            port='5432'
        )
        self.user = User(self.db)

    def main_menu(self):
        while True:
            print("\n--- Welcome to School Management System ---")
            print("1. Register")
            print("2. Log in")
            print("3. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                self.user.register()
            elif choice == '2':
                self.user.login()
            elif choice == '3':
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

        self.db.close()

if __name__ == "__main__":
    try:
        system = SchoolManagementSystem()
        system.main_menu()
    except Exception as e:
        print(f"Unexpected error: {e}")
