#connectdatabase
import psycopg2

def connect_to_db():
    try:
        conn = psycopg2.connect(
            host='localhost',           # PostgreSQL host
            database='regftu',           # PostgreSQL database name
            user='postgres',            # PostgreSQL username
            password='admin',           # PostgreSQL password
            port='5432'                 # PostgreSQL default port
        )
        return conn, conn.cursor()
    except Exception as e:
        print(f"Database connection error: {e}")
        exit()

conn, cursor = connect_to_db()
# Registration
def register_user():
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

            cursor.execute('INSERT INTO Users (name, username, password, role) VALUES (%s, %s, %s, %s)', 
                           (name, username, password, role))
            conn.commit()
            print(f"{role} registered successfully.")
            break
        except errors.UniqueViolation:
            conn.rollback()
            print("Username already exists. Please choose another.")
        except Exception as e:
            print(f"Error: {e}")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                break

# Login
def login():
    while True:
        try:
            username = input("Username: ")
            password = input("Password: ")

            cursor.execute('SELECT * FROM Users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()

            if user:
                print(f"\nWelcome {user[1]}! Logged in as {user[4]}.")
                if user[4] == 'Teacher':
                    teacher_menu(user)
                elif user[4] == 'Student':
                    student_menu(user)
                break
            else:
                print("Invalid credentials.")
                retry = input("Do you want to try logging in again? (y/n): ")
                if retry.lower() != 'y':
                    break
        except Exception as e:
            print(f"Error: {e}")
            break

# Teacher Menu
def teacher_menu(user):
    while True:
        try:
            print("\n--- Teacher Menu ---")
            print("1. View Subjects and Students")
            print("2. Add Subject")
            print("3. Add/Edit Student Grades")
            print("4. View Teaching Schedule")
            print("5. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                cursor.execute('SELECT id, name, description, schedule FROM Subjects WHERE teacher_id = %s', (user[0],))
                subjects = cursor.fetchall()
                if not subjects:
                    print("No subjects found.")
                else:
                    for subj in subjects:
                        print(f"\nSubject: {subj[1]}\nDescription: {subj[2]}\nSchedule: {subj[3]}")
                        cursor.execute('''
                            SELECT u.name FROM Enrollments e
                            JOIN Users u ON e.student_id = u.id
                            WHERE e.subject_id = %s
                        ''', (subj[0],))
                        students = cursor.fetchall()
                        print("Students:")
                        for student in students:
                            print(f"- {student[0]}")

            elif choice == '2':
                name = input("Subject Name: ")
                description = input("Subject Description: ")
                schedule = input("Schedule (e.g., Monday 13.00-15.00): ")
                cursor.execute('INSERT INTO Subjects (name, description, schedule, teacher_id) VALUES (%s, %s, %s, %s)', 
                               (name, description, schedule, user[0]))
                conn.commit()
                print("Subject added successfully.")

            elif choice == '3':
                cursor.execute('SELECT s.id, s.name FROM Subjects s WHERE s.teacher_id = %s', (user[0],))
                subjects = cursor.fetchall()
                if not subjects:
                    print("No subjects found.")
                    continue

                print("Subjects:")
                for subj in subjects:
                    print(f"{subj[0]}: {subj[1]}")
                
                try:
                    subject_id = int(input("Enter subject ID to edit grades: "))
                    cursor.execute('''
                        SELECT e.id, u.name, e.grade FROM Enrollments e
                        JOIN Users u ON e.student_id = u.id
                        WHERE e.subject_id = %s
                    ''', (subject_id,))
                    enrollments = cursor.fetchall()

                    if not enrollments:
                        print("No students enrolled in this subject.")
                        continue

                    for enrollment in enrollments:
                        print(f"{enrollment[0]}: {enrollment[1]} - Grade: {enrollment[2]}")
                        edit = input("Edit grade? (y/n): ")
                        if edit.lower() == 'y':
                            new_grade = float(input("Enter new grade: "))
                            cursor.execute('UPDATE Enrollments SET grade = %s WHERE id = %s', 
                                           (new_grade, enrollment[0]))
                            conn.commit()
                            print("Grade updated.")
                except ValueError:
                    print("Invalid subject ID.")

            elif choice == '4':
                cursor.execute('SELECT schedule, name FROM Subjects WHERE teacher_id = %s ORDER BY schedule', (user[0],))
                schedule = cursor.fetchall()
                if not schedule:
                    print("No schedule available.")
                else:
                    print("\nTeaching Schedule:")
                    for sch in schedule:
                        print(f"{sch[0]} ({sch[1]})")

            elif choice == '5':
                print("Logged out.")
                break
            else:
                print("Invalid option. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                break

# Student Menu
def student_menu(user):
    while True:
        try:
            print("\n--- Student Menu ---")
            print("1. View Enrolled Subjects")
            print("2. View Grades")
            print("3. View Class Schedule")
            print("4. Add/Drop Subject")
            print("5. Logout")
            choice = input("Select an option: ")

            if choice == '1':
                cursor.execute('''
                    SELECT s.name, s.description, s.schedule 
                    FROM Subjects s
                    JOIN Enrollments e ON s.id = e.subject_id
                    WHERE e.student_id = %s
                ''', (user[0],))
                subjects = cursor.fetchall()
                if subjects:
                    print("\n--- Enrolled Subjects ---")
                    for idx, subj in enumerate(subjects, 1):
                        print(f"{idx}. {subj[0]}\n   Schedule: {subj[2]}\n   Description: {subj[1]}\n")
                else:
                    print("No enrolled subjects.")

            elif choice == '2':
                cursor.execute('''
                    SELECT s.name, e.grade 
                    FROM Subjects s
                    JOIN Enrollments e ON s.id = e.subject_id
                    WHERE e.student_id = %s
                ''', (user[0],))
                grades = cursor.fetchall()

                if grades:
                    print("\n--- Your Grades ---")
                    for subj, grade in grades:
                        print(f"{subj}: {grade if grade is not None else 'Not graded yet'}")
                else:
                    print("No grades available.")

            elif choice == '3':
                cursor.execute('''
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
                ''', (user[0],))
                schedule = cursor.fetchall()

                if schedule:
                    print("\n--- Your Class Schedule ---")
                    for sch, name in schedule:
                        print(f"{sch} ({name})")
                else:
                    print("No schedule available.")

            elif choice == '4':
                while True:
                    print("\n--- Add/Drop Subject ---")
                    print("1. Add Subject")
                    print("2. Drop Subject")
                    print("3. Back to Student Menu")
                    sub_choice = input("Select an option: ")

                    if sub_choice == '1':
                        cursor.execute('SELECT id, name FROM Subjects')
                        subjects = cursor.fetchall()

                        print("\n--- Available Subjects ---")
                        for subj in subjects:
                            print(f"{subj[0]}: {subj[1]}")

                        try:
                            subject_id = int(input("Enter the subject ID to add: "))
                            cursor.execute('SELECT * FROM Enrollments WHERE student_id = %s AND subject_id = %s', (user[0], subject_id))

                            if cursor.fetchone():
                                print("You are already enrolled in this subject.")
                            else:
                                cursor.execute('INSERT INTO Enrollments (student_id, subject_id) VALUES (%s, %s)', 
                                               (user[0], subject_id))
                                conn.commit()
                                print("Subject added successfully.")
                        except ValueError:
                            print("Invalid input. Please enter a valid subject ID.")

                    elif sub_choice == '2':
                        cursor.execute('''
                            SELECT s.id, s.name 
                            FROM Subjects s
                            JOIN Enrollments e ON s.id = e.subject_id
                            WHERE e.student_id = %s
                        ''', (user[0],))
                        enrolled_subjects = cursor.fetchall()

                        if enrolled_subjects:
                            print("\n--- Enrolled Subjects ---")
                            for subj in enrolled_subjects:
                                print(f"{subj[0]}: {subj[1]}")

                            try:
                                subject_id = int(input("Enter the subject ID to drop: "))
                                cursor.execute('DELETE FROM Enrollments WHERE student_id = %s AND subject_id = %s', 
                                               (user[0], subject_id))
                                conn.commit()
                                print("Subject dropped successfully.")
                            except ValueError:
                                print("Invalid input. Please enter a valid subject ID.")
                        else:
                            print("You are not enrolled in any subjects.")

                    elif sub_choice == '3':
                        break
                    else:
                        print("Invalid option. Please try again.")

            elif choice == '5':
                print("Logged out.")
                break
            else:
                print("Invalid option. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                break

# Main Menu
def main_menu():
    while True:
        try:
            print("\n--- Welcome to School Management System ---")
            print("1. Register")
            print("2. Log in")
            print("3. Exit")
            choice = input("Select an option: ")

            if choice == '1':
                register_user()
            elif choice == '2':
                login()
            elif choice == '3':
                print("Thank you for using the system. Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")

        except Exception as e:
            print(f"An error occurred: {e}")
            retry = input("Do you want to try again? (y/n): ")
            if retry.lower() != 'y':
                break

if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        cursor.close()
        conn.close()
        print("Database connection closed.")
