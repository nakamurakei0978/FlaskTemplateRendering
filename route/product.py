from flask import Blueprint, render_template, request, redirect, current_app
from werkzeug.utils import secure_filename
import os
from config import execute_query

students = Blueprint('students', __name__)


# ** filter db and get all data and throw to student list page
@students.route('/admin/student')
def student():
    # Get the page number from the query parameters (default to 1 if not present)
    page = request.args.get('page', 1, type=int)

    # Define the number of records per page
    records_per_page = 8

    # Calculate the offset based on the current page
    offset = (page - 1) * records_per_page

    # Use the helper function to execute the query
    rows = execute_query("SELECT * FROM student LIMIT ? OFFSET ?", (records_per_page, offset))

    # Calculate the total number of pages
    total_records = execute_query("SELECT COUNT(*) FROM student")[0][0]
    total_pages = (total_records // records_per_page) + (total_records % records_per_page > 0)

    return render_template('admin/student/index.html', rows=rows, page=page, total_pages=total_pages)


# ** load to add student page
@students.route('/admin/add_student')
def add_student():
    return render_template('admin/student/add_student.html')


# ** student added to db
@students.route('/admin/student_added', methods=['POST'])
def student_added():
    if request.method == "POST":
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            birthday = request.form['birthday']
            gender = request.form['gender']
            email = request.form['email']
            phone = request.form['phone']
            subject = request.form['subject']

            if subject == 'Select subject':
                subject = ''

            image = request.files.get('image_upload')

            address = request.form['address']
            # check if user input image or not
            if image:
                # Check the file extension
                _, extension = os.path.splitext(image.filename)
                if extension.lower() not in ['.jpg', '.png', '.jfif', '.svg', '.jpeg', '.gif']:
                    return 'Invalid file type. Only jpg, png, and jfif files are allowed.', 400

                # Check the file size (2MB = 2 * 1024 * 1024 bytes)
                if image.content_length > 2 * 1024 * 1024:
                    return 'File size is too large. The maximum file size is 2MB.', 400

                # Save the image to the uploads folder, with fisrtname_lastname.extension as the filename
                filename = secure_filename(f"{firstname}_{lastname}{extension}")
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                query = "INSERT INTO student (firstname,lastname,birthday,gender," \
                        "email,phone,subject,image,address) VALUES (?,?,?,?,?,?,?,?,?)"
                params = (firstname, lastname, birthday, gender, email, phone, subject, filename, address)
            else:
                query = "INSERT INTO student (firstName,lastName,birthday,gender," \
                        "email,phone,subject,address) VALUES (?,?,?,?,?,?,?,?)"
                params = (firstname, lastname, birthday, gender, email, phone, subject, address)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/student')
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student detail from student page or detail page to filter db and throw to edit page
@students.route('/admin/edit_student', methods=['GET', 'POST'])
def edit_student():
    if request.method == 'POST':
        student_id = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM student WHERE id = ?"
        rows = execute_query(query, (student_id,))

        return render_template('admin/student/edit_student.html', rows=rows, page=page)
    else:
        return redirect('/admin/student')


# ** Student edit or update to db
@students.route('/admin/student_edited', methods=['POST'])
def student_edited():
    if request.method == "POST":
        try:
            sid = request.form['id']
            page_id = request.form['page_id']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            birthday = request.form['birthday']
            gender = request.form['gender']
            email = request.form['email']
            phone = request.form['phone']
            subject = request.form['subject']
            address = request.form['address']

            image = request.files.get('image_upload')

            # check if user input image or not
            if image:
                # Check the file extension
                _, extension = os.path.splitext(image.filename)
                if extension.lower() not in ['.jpg', '.png', '.jfif', '.svg', '.jpeg', '.gif']:
                    return 'Invalid file type. Only jpg, png, and jfif files are allowed.', 400

                # Check the file size (2MB = 2 * 1024 * 1024 bytes)
                if image.content_length > 2 * 1024 * 1024:
                    return 'File size is too large. The maximum file size is 2MB.', 400

                # Get the old image filename from the database
                old_image_query = "SELECT image FROM student WHERE id = ?"
                old_image_filename = execute_query(old_image_query, (sid,), is_insert=False)[0]['image']

                # Delete the old image file
                if old_image_filename:
                    old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_image_filename)
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)

                # Save the image to the uploads folder, with fisrtname_lastname.extension as the filename
                filename = secure_filename(f"{firstname}_{lastname}{extension}")
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                query = f"UPDATE student SET " \
                        f"firstName = ?, " \
                        f"lastName = ?, " \
                        f"birthday = ?, " \
                        f"gender = ?, " \
                        f"email = ?, " \
                        f"phone = ?, " \
                        f"subject = ?, " \
                        f"image = ?, " \
                        f"address = ? " \
                        f"WHERE id = ?"
                params = (firstname, lastname, birthday, gender, email, phone, subject, filename, address, sid)
            else:
                query = f"UPDATE student SET " \
                        f"firstName = ?, " \
                        f"lastName = ?, " \
                        f"birthday = ?, " \
                        f"gender = ?, " \
                        f"email = ?, " \
                        f"phone = ?, " \
                        f"subject = ?, " \
                        f"address = ? " \
                        f"WHERE id = ?"
                params = (firstname, lastname, birthday, gender, email, phone, subject, address, sid)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/student?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student details from student page to filter db and throw to detail page
@students.route('/admin/detail_student', methods=['GET', 'POST'])
def detail_student():
    if request.method == 'POST':
        student_id = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM student WHERE id = ?"
        rows = execute_query(query, (student_id,))

        return render_template('admin/student/detail_student.html', rows=rows, page=page)
    else:
        return redirect('/admin/student')


# ** Student delete on db
@students.route('/admin/delete_student', methods=['POST'])
def delete_student():
    if request.method == "POST":
        try:
            sid = request.form['id']
            page_id = request.form['page_id']
            image = request.form['image_upload']

            # Delete the old image file if it's not the default image
            if image != 'default_img':
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image)
                if os.path.isfile(image_path):
                    os.remove(image_path)

            query = f"DELETE FROM student WHERE id = ?"
            execute_query(query, (sid,), is_insert=True)

            return redirect('/admin/student?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"
