import mysql.connector
import csv
import os

# Student Management System
# Author: Bikita Hait | MCA Graduate | Python Full Stack Developer

class StudentManagementSystem:
    def __init__(self):
        print("\n====== STUDENT MANAGEMENT SYSTEM ======")
        password = input("Enter MySQL password: ")
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password=password,
                database="studentdb",
                auth_plugin="mysql_native_password"
            )
            self.cursor = self.db.cursor()
            self.create_tables()
            print("Database connected successfully!")
        except mysql.connector.Error as e:
            print(f"Connection failed: {e}")
            exit()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone VARCHAR(15) UNIQUE NOT NULL,
            course VARCHAR(100) NOT NULL,
            age INT NOT NULL
        )
        """)
        self.db.commit()

    def add_student(self):
        print("\n--- Add Student ---")
        name = input("Enter student name: ").strip()
        if not name:
            print("Name cannot be empty")
            return

        email = input("Enter email: ").strip()
        if "@" not in email or "." not in email:
            print("Invalid email format")
            return
        self.cursor.execute("SELECT * FROM students WHERE email=%s", (email,))
        if self.cursor.fetchone():
            print("Email already registered")
            return

        phone = input("Enter phone number: ").strip()
        if not phone.isdigit() or len(phone) != 10:
            print("Invalid phone number (must be 10 digits)")
            return
        self.cursor.execute("SELECT * FROM students WHERE phone=%s", (phone,))
        if self.cursor.fetchone():
            print("Phone number already registered")
            return

        course = input("Enter course (e.g. MCA, BCA, BSc): ").strip().upper()

        age = input("Enter age: ").strip()
        if not age.isdigit() or not (15 <= int(age) <= 40):
            print("Invalid age (must be between 15 and 40)")
            return

        self.cursor.execute(
            "INSERT INTO students (name, email, phone, course, age) VALUES (%s, %s, %s, %s, %s)",
            (name, email, phone, course, int(age))
        )
        self.db.commit()
        print(f"Student '{name}' added successfully!")

    def view_all_students(self):
        print("\n--- All Students ---")
        self.cursor.execute("SELECT id, name, email, phone, course, age FROM students ORDER BY name")
        students = self.cursor.fetchall()
        if not students:
            print("No students found")
            return
        print(f"Total Students: {len(students)}\n")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<12} {'Course':<10} {'Age'}")
        print("-" * 85)
        for s in students:
            print(f"{s[0]:<5} {s[1]:<20} {s[2]:<30} {s[3]:<12} {s[4]:<10} {s[5]}")

    def search_student(self):
        print("\n--- Search Student ---")
        keyword = input("Enter name or email to search: ").strip()
        self.cursor.execute(
            "SELECT id, name, email, phone, course, age FROM students WHERE name LIKE %s OR email LIKE %s",
            (f"%{keyword}%", f"%{keyword}%")
        )
        results = self.cursor.fetchall()
        if not results:
            print("No student found")
            return
        print(f"\nFound {len(results)} result(s):\n")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<12} {'Course':<10} {'Age'}")
        print("-" * 85)
        for s in results:
            print(f"{s[0]:<5} {s[1]:<20} {s[2]:<30} {s[3]:<12} {s[4]:<10} {s[5]}")

    def update_student(self):
        print("\n--- Update Student ---")
        sid = input("Enter student ID to update: ").strip()
        if not sid.isdigit():
            print("Invalid ID")
            return
        self.cursor.execute("SELECT * FROM students WHERE id=%s", (sid,))
        student = self.cursor.fetchone()
        if not student:
            print("Student not found")
            return
        print(f"\nCurrent Details:")
        print(f"Name: {student[1]} | Email: {student[2]} | Phone: {student[3]} | Course: {student[4]} | Age: {student[5]}")
        print("\nWhat to update?")
        print("1. Name")
        print("2. Phone")
        print("3. Course")
        print("4. Age")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            new_val = input("Enter new name: ").strip()
            if not new_val:
                print("Name cannot be empty")
                return
            self.cursor.execute("UPDATE students SET name=%s WHERE id=%s", (new_val, sid))
        elif choice == "2":
            new_val = input("Enter new phone: ").strip()
            if not new_val.isdigit() or len(new_val) != 10:
                print("Invalid phone number")
                return
            self.cursor.execute("SELECT * FROM students WHERE phone=%s AND id!=%s", (new_val, sid))
            if self.cursor.fetchone():
                print("Phone already registered")
                return
            self.cursor.execute("UPDATE students SET phone=%s WHERE id=%s", (new_val, sid))
        elif choice == "3":
            new_val = input("Enter new course: ").strip().upper()
            self.cursor.execute("UPDATE students SET course=%s WHERE id=%s", (new_val, sid))
        elif choice == "4":
            new_val = input("Enter new age: ").strip()
            if not new_val.isdigit() or not (15 <= int(new_val) <= 40):
                print("Invalid age")
                return
            self.cursor.execute("UPDATE students SET age=%s WHERE id=%s", (int(new_val), sid))
        else:
            print("Invalid choice")
            return
        self.db.commit()
        print("Student updated successfully!")

    def delete_student(self):
        print("\n--- Delete Student ---")
        sid = input("Enter student ID to delete: ").strip()
        if not sid.isdigit():
            print("Invalid ID")
            return
        self.cursor.execute("SELECT name FROM students WHERE id=%s", (sid,))
        student = self.cursor.fetchone()
        if not student:
            print("Student not found")
            return
        confirm = input(f"Are you sure you want to delete '{student[0]}'? (yes/no): ").lower()
        if confirm == "yes":
            self.cursor.execute("DELETE FROM students WHERE id=%s", (sid,))
            self.db.commit()
            print(f"Student '{student[0]}' deleted successfully!")
        else:
            print("Cancelled")

    def view_by_course(self):
        print("\n--- View by Course ---")
        self.cursor.execute("SELECT DISTINCT course FROM students ORDER BY course")
        courses = self.cursor.fetchall()
        if not courses:
            print("No courses found")
            return
        for i, c in enumerate(courses):
            print(f"{i+1}. {c[0]}")
        choice = input("Enter course number: ").strip()
        if not choice.isdigit():
            print("Invalid input")
            return
        choice = int(choice)
        if choice < 1 or choice > len(courses):
            print("Invalid choice")
            return
        selected = courses[choice - 1][0]
        self.cursor.execute(
            "SELECT id, name, email, phone, age FROM students WHERE course=%s ORDER BY name",
            (selected,)
        )
        students = self.cursor.fetchall()
        print(f"\n--- {selected} Students --- Total: {len(students)}\n")
        print(f"{'ID':<5} {'Name':<20} {'Email':<30} {'Phone':<12} {'Age'}")
        print("-" * 75)
        for s in students:
            print(f"{s[0]:<5} {s[1]:<20} {s[2]:<30} {s[3]:<12} {s[4]}")

    def export_to_csv(self):
        print("\n--- Export to CSV ---")
        self.cursor.execute("SELECT id, name, email, phone, course, age FROM students ORDER BY name")
        students = self.cursor.fetchall()
        if not students:
            print("No students to export")
            return
        filename = "students_export.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Name", "Email", "Phone", "Course", "Age"])
            writer.writerows(students)
        print(f"Exported {len(students)} records successfully!")
        print(f"File saved at: {os.path.abspath(filename)}")

    def main(self):
        while True:
            print("\n====== STUDENT MANAGEMENT SYSTEM ======")
            print("1. Add Student")
            print("2. View All Students")
            print("3. Search Student")
            print("4. Update Student")
            print("5. Delete Student")
            print("6. View by Course")
            print("7. Export to CSV")
            print("8. Exit")
            choice = input("\nEnter your choice: ").strip()
            if choice == "1":
                self.add_student()
            elif choice == "2":
                self.view_all_students()
            elif choice == "3":
                self.search_student()
            elif choice == "4":
                self.update_student()
            elif choice == "5":
                self.delete_student()
            elif choice == "6":
                self.view_by_course()
            elif choice == "7":
                self.export_to_csv()
            elif choice == "8":
                print("\nThank You! Goodbye!")
                self.db.close()
                break
            else:
                print("Invalid choice. Please try again.")

run = StudentManagementSystem()
run.main()