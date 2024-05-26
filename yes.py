import atexit

import mysql.connector
from flask import Flask, render_template, request

app = Flask(__name__)

# establishing database connection
db_connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Sunshine4.",
    database="attendance_system"
)
cursor = db_connection.cursor()

#adding a student
def add_student(student_name):
    query = "INSERT INTO students (student_name) VALUES (%s)"
    check_query = "SELECT * FROM students WHERE student_name = %s"

    cursor.execute(check_query, (student_name,))
    existing_student = cursor.fetchone()

    if existing_student:
        return f"Student '{student_name}' already exists. <a href='/'>GO BACK</a>"
    else:
        cursor.execute(query, (student_name,))
        db_connection.commit()
        return f"Student '{student_name}' was added successfully. <a href='/'>GO BACK</a>"


#modifying a student name
def modify_student(old_name, new_name):
    query = "UPDATE students SET student_name = %s WHERE student_name = %s"
    check_query = "SELECT * FROM students WHERE student_name = %s"

    cursor.execute(check_query, (old_name,))
    existing_student = cursor.fetchone()

    if existing_student:
        cursor.execute(query, (new_name, old_name))
        db_connection.commit()
        return f"The student's information has been updated successfully. <a href='/'>GO BACK</a>"
    else:
        return f"Error: Student '{old_name}' does not exist. <a href='/'>GO BACK</a>"

# deleting a student function
def delete_student(student_name):
    delete_attendance_query = "DELETE FROM attendance WHERE student_id IN " \
                              "(SELECT student_id FROM students WHERE student_name = %s)"
    check_query = "SELECT * FROM students WHERE student_name = %s"

    cursor.execute(check_query, (student_name,))
    existing_student = cursor.fetchone()

    if existing_student:
        cursor.execute(delete_attendance_query, (student_name,))
        cursor.execute("DELETE FROM students WHERE student_name = %s", (student_name,))
        db_connection.commit()
        return f"The student '{student_name}' has been deleted successfully. <a href='/'>GO BACK</a>"
    else:
        return f"Error: Student '{student_name}' does not exist. <a href='/'>GO BACK</a>"


# adding a course
def add_course(course_name):
    query = "INSERT INTO courses (course_name) VALUES (%s)"
    check_query = "SELECT * FROM courses WHERE course_name = %s"

    cursor.execute(check_query, (course_name,))
    existing_course = cursor.fetchone()

    if existing_course:
        return f"The course '{course_name}' already exists. <a href='/'>GO BACK</a>"
    else:
        cursor.execute(query, (course_name,))
        db_connection.commit()
        return f"Course '{course_name}' was added successfully. <a href='/'>GO BACK</a>"


# modifying a course
def modify_course(old_name, new_name):
    query = "UPDATE courses SET course_name = %s WHERE course_name = %s"
    check_query = "SELECT * FROM courses WHERE course_name = %s"

    cursor.execute(check_query, (old_name,))
    existing_course = cursor.fetchone()

    if existing_course:
        cursor.execute(query, (new_name, old_name))
        db_connection.commit()
        return f"The course information has been updated successfully. <a href='/'>GO BACK</a>"
    else:
        return f"Error: Course '{old_name}' does not exist. <a href='/'>GO BACK</a>"

# deleting a course
def delete_course(course_name):
    delete_attendance_query = "DELETE FROM attendance WHERE course_id IN " \
                              "(SELECT course_id FROM courses WHERE course_name = %s)"
    check_query = "SELECT * FROM courses WHERE course_name = %s"

    cursor.execute(check_query, (course_name,))
    existing_course = cursor.fetchone()

    if existing_course:
        cursor.execute(delete_attendance_query, (course_name,))
        cursor.execute("DELETE FROM courses WHERE course_name = %s", (course_name,))
        db_connection.commit()
        return f"The course '{course_name}' has been deleted successfully. <a href='/'>GO BACK</a>"
    else:
        return f"Error: Course '{course_name}' does not exist. <a href='/'>GO BACK</a>"

#help function to retrieve all students
def get_students_from_database():
    try:
        get_students_query = "SELECT student_id, student_name FROM students"
        cursor.execute(get_students_query)
        students = cursor.fetchall()
        return students
    except Exception as e:
        print(f"An error occurred while fetching students: {e}")
        return []

#help function to get all courses id
def get_course_id(course_name):
    get_course_id_query = "SELECT course_id FROM courses WHERE course_name = %s"
    cursor.execute(get_course_id_query, (course_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

#marking an attendance
def mark_attendance(course_name, attendance_date, form_data):
    try:
        check_query_course = "SELECT * FROM courses WHERE course_name = %s"
        cursor.execute(check_query_course, (course_name,))
        existing_course = cursor.fetchone()

        if existing_course:
            for key, value in form_data.items():
                if key.startswith("attendance_"):
                    try:
                        student_id = int(key.replace("attendance_", ""))
                    except ValueError:
                        print(f"Error: Invalid format for student_id in key '{key}'")
                        continue

                    status = value
                    check_query_student = "SELECT * FROM students WHERE student_id = %s"
                    cursor.execute(check_query_student, (student_id,))
                    existing_student = cursor.fetchone()

                    if existing_student:
                        mark_attendance_query = "INSERT INTO attendance (student_id, course_id, attendance_date, status) " \
                                                "VALUES (%s, %s, %s, %s)"
                        cursor.execute(mark_attendance_query, (student_id, existing_course[0], attendance_date, status))
                    else:
                        print(f"Error: Student with ID '{student_id}' does not exist.")
                        continue

            db_connection.commit()
            return f"The attendance has been marked successfully for {course_name} on {attendance_date}."
        else:
            return f"Error: Course '{course_name}' does not exist."
    except Exception as e:
        return f"An unexpected error occurred: {e}"


#calculate if a student has sufficient attendances or not.
def calculate_pass_status(student_name, course_name):
    try:
        check_query_student = "SELECT * FROM students WHERE student_name = %s"
        cursor.execute(check_query_student, (student_name,))
        existing_student = cursor.fetchone()

        check_query_course = "SELECT * FROM courses WHERE course_name = %s"
        cursor.execute(check_query_course, (course_name,))
        existing_course = cursor.fetchone()

        if existing_student and existing_course:
            get_attendance_query = "SELECT COUNT(*) FROM attendance " \
                                   "WHERE student_id = %s AND course_id = %s AND status = 'Present'"
            cursor.execute(get_attendance_query, (existing_student[0], existing_course[0]))
            present_count = cursor.fetchone()[0]

            return present_count >= 5
        else:
            print(f"Error: Student '{student_name}' or Course '{course_name}' does not exist.")
            return None
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None



#app routes for the pages

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student_route():
    if request.method == 'POST':
        student_name = request.form['student_name']
        result_message = add_student(student_name)
        return result_message

    return render_template('add_student.html')

@app.route('/modify_student', methods=['GET', 'POST'])
def modify_student_route():
    if request.method == 'POST':
        old_name = request.form['old_name']
        new_name = request.form['new_name']
        result_message = modify_student(old_name, new_name)
        return result_message

    return render_template('modify_student.html')

@app.route('/delete_student', methods=['GET', 'POST'])
def delete_student_route():
    if request.method == 'POST':
        student_name = request.form['student_name']
        result_message = delete_student(student_name)
        return result_message

    return render_template('delete_student.html')
@app.route('/add_course', methods=['GET', 'POST'])
def add_course_route():
    if request.method == 'POST':
        course_name = request.form['course_name']
        result_message = add_course(course_name)
        return result_message

    return render_template('add_course.html')

@app.route('/modify_course', methods=['GET', 'POST'])
def modify_course_route():
    if request.method == 'POST':
        old_name = request.form['old_name']
        new_name = request.form['new_name']
        result_message = modify_course(old_name, new_name)
        return result_message

    return render_template('modify_course.html')
@app.route('/delete_course', methods=['GET', 'POST'])
def delete_course_route():
    if request.method == 'POST':
        course_name = request.form['course_name']
        result_message = delete_course(course_name)
        return result_message

    return render_template('delete_course.html')

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance_route():
    if request.method == 'POST':
        course_name = request.form['course_name']
        attendance_date = request.form['attendance_date']
        result_message = mark_attendance(course_name, attendance_date, request.form)
        return result_message

    students = get_students_from_database()

    return render_template('mark_attendance.html', students=students)


@app.route('/view_student_attendance', methods=['GET', 'POST'])
def view_student_attendance_route():
    try:
        if request.method == 'POST':
            student_name = request.form['student_name']
            get_student_query = "SELECT * FROM students WHERE student_name = %s"
            cursor.execute(get_student_query, (student_name,))
            existing_student = cursor.fetchone()

            if existing_student:
                print("Student ID:", existing_student[0])

                get_attendance_query = """
                    SELECT c.course_name, a.attendance_date, a.status
                    FROM attendance a
                    JOIN courses c ON a.course_id = c.course_id
                    WHERE a.student_id = %s
                    ORDER BY a.attendance_date
                """
                cursor.execute(get_attendance_query, (existing_student[0],))
                attendance_records = cursor.fetchall()

                return render_template('view_student_attendance.html', student_name=existing_student[1],
                                       attendance_records=attendance_records)
            else:
                return render_template('view_student_attendance.html', student_name=None, attendance_records=None,
                                       error_message="Student has not found.")

        return render_template('view_student_attendance.html', student_name=None, attendance_records=None,
                               error_message=None)

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return f"MySQL Error: {err}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"


@app.route('/check_pass_status', methods=['GET', 'POST'])
def check_pass_status_route():
    try:
        if request.method == 'POST':
            student_name = request.form['student_name']
            course_name = request.form['course_name']

            pass_status = calculate_pass_status(student_name, course_name)
            return render_template('check_pass_status.html', student_name=student_name, course_name=course_name,
                                   pass_status=pass_status)

        return render_template('check_pass_status.html', student_name=None, course_name=None, pass_status=None,
                               error_message=None)

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return f"MySQL Error: {err}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}"


@app.route('/modify_attendance', methods=['GET', 'POST'])
def modify_attendance_route():
    try:
        if request.method == 'POST':
            course_name = request.form['course_name']
            attendance_date = request.form['attendance_date']
            get_students_query = "SELECT student_id, student_name FROM students"
            cursor.execute(get_students_query)
            students = cursor.fetchall()

            for student_id, student_name in students:
                attendance_status = request.form.get(f'attendance_{student_id}')
                if attendance_status:
                    check_attendance_query = "SELECT * FROM attendance WHERE student_id = %s AND course_id = (SELECT course_id FROM courses WHERE course_name = %s) AND attendance_date = %s"
                    cursor.execute(check_attendance_query, (student_id, course_name, attendance_date))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        update_attendance_query = "UPDATE attendance SET status = %s WHERE student_id = %s AND course_id = (SELECT course_id FROM courses WHERE course_name = %s) AND attendance_date = %s"
                        cursor.execute(update_attendance_query,
                                       (attendance_status, student_id, course_name, attendance_date))
                    else:
                        insert_attendance_query = "INSERT INTO attendance (student_id, course_id, attendance_date, status) VALUES (%s, (SELECT course_id FROM courses WHERE course_name = %s), %s, %s)"
                        cursor.execute(insert_attendance_query,
                                       (student_id, course_name, attendance_date, attendance_status))

            db_connection.commit()
            return "Attendance updated successfully! <a href='/'>GO BACK</a>"

        get_courses_query = "SELECT course_name FROM courses"
        cursor.execute(get_courses_query)
        courses = [course[0] for course in cursor.fetchall()]

        get_dates_query = "SELECT DISTINCT attendance_date FROM attendance"
        cursor.execute(get_dates_query)
        dates = [date[0].strftime('%Y-%m-%d') for date in cursor.fetchall()]

        students_query = "SELECT student_id, student_name FROM students"
        cursor.execute(students_query)
        students = cursor.fetchall()

        return render_template('modify_attendance.html', courses=courses, dates=dates, students=students,
                               error_message=None)

    except Exception as e:
        return render_template('modify_attendance.html', courses=None, dates=None, students=None,
                               error_message=f"An unexpected error occurred: {e}")

@app.route('/delete_attendance', methods=['GET', 'POST'])
def delete_attendance_route():
    try:
        if request.method == 'POST':
            course_name = request.form['course_name']
            attendance_date = request.form['attendance_date']

            check_course_date_query = "SELECT * FROM attendance WHERE course_id = (SELECT course_id FROM courses WHERE course_name = %s) AND attendance_date = %s"
            cursor.execute(check_course_date_query, (course_name, attendance_date))
            existing_records = cursor.fetchall()

            if existing_records:
                delete_attendance_query = "DELETE FROM attendance WHERE course_id = (SELECT course_id FROM courses WHERE course_name = %s) AND attendance_date = %s"
                cursor.execute(delete_attendance_query, (course_name, attendance_date))

                db_connection.commit()
                return "Attendance records deleted successfully! <a href='/'>GO BACK</a>"
            else:
                return "No attendance records found. <a href='/'>GO BACK</a>"


        get_courses_query = "SELECT course_name FROM courses"
        cursor.execute(get_courses_query)
        courses = [course[0] for course in cursor.fetchall()]

        get_dates_query = "SELECT DISTINCT attendance_date FROM attendance"
        cursor.execute(get_dates_query)
        dates = [date[0].strftime('%Y-%m-%d') for date in cursor.fetchall()]

        return render_template('delete_attendance.html', courses=courses, dates=dates, error_message=None)

    except Exception as e:
        return render_template('delete_attendance.html', courses=None, dates=None, error_message=f"An unexpected error occurred: {e}")

def close_database_connection():
    cursor.close()
    db_connection.close()
atexit.register(close_database_connection)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

