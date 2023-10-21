import random
from datetime import datetime
from unicodedata import decimal

from flask import Blueprint, render_template, request, redirect, current_app
from werkzeug.utils import secure_filename
import os
from config import execute_query

customers = Blueprint('customers', __name__)


# ** filter db and get all data and throw to student list page
@customers.route('/admin/customer')
def customer():
    # Get the page number from the query parameters (default to 1 if not present)
    page = request.args.get('page', 1, type=int)

    # Define the number of records per page
    records_per_page = 7

    # Calculate the offset based on the current page
    offset = (page - 1) * records_per_page

    # Use the helper function to execute the query
    rows = execute_query("SELECT * FROM customer LIMIT ? OFFSET ?",
                         (records_per_page, offset))

    # Calculate the total number of pages
    total_records = execute_query("SELECT COUNT(*) FROM customer")[0][0]
    total_pages = (total_records // records_per_page) + (total_records % records_per_page > 0)

    return render_template('admin/customer/index.html', rows=rows, page=page, total_pages=total_pages)


# ** load to add student page
@customers.route('/admin/add_customer')
def add_customer():
    return render_template('admin/customer/add_customer.html')


# ** student added to db
@customers.route('/admin/customer_added', methods=['POST'])
def customer_added():
    if request.method == "POST":
        try:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            status = request.form['status']
            rnd = random.random()

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

                # Save the image to the uploads folder, with fisrtname_lastname.extension as the filename
                filename = secure_filename(f"{firstname}_{rnd}{extension}")
                image.save(os.path.join(current_app.config['CUSTOMER_UPLOAD_FOLDER'], filename))

                query = "INSERT INTO customer (firstname,lastname,status, image) VALUES (?,?,?,?)"
                params = (firstname, lastname, status, filename)
            else:
                query = "INSERT INTO customer (firstname,lastname,status) VALUES (?,?,?)"
                params = (firstname, lastname, status)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/customer')
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student detail from student page or detail page to filter db and throw to edit page
@customers.route('/admin/edit_customer', methods=['GET', 'POST'])
def edit_customer():
    if request.method == 'POST':
        cid = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM customer WHERE id = ?"
        rows = execute_query(query, (cid,))

        return render_template('admin/customer/edit_customer.html', rows=rows, page=page)
    else:
        return redirect('/admin/customer')


# ** Student edit or update to db
@customers.route('/admin/customer_edited', methods=['POST'])
def customer_edited():
    if request.method == "POST":
        try:
            cid = request.form['id']
            page_id = request.form['page_id']
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            status = request.form['status']
            rnd = random.random()

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
                old_image_query = "SELECT image FROM customer WHERE id = ?"
                old_image_filename = execute_query(old_image_query, (cid,), is_insert=False)[0]['image']

                # Delete the old image file
                if old_image_filename:
                    old_image_path = os.path.join(current_app.config['CUSTOMER_UPLOAD_FOLDER'], old_image_filename)
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)

                # Save the image to the uploads folder, with fisrtname_lastname.extension as the filename
                filename = secure_filename(f"{firstname}_{rnd}{extension}")
                image.save(os.path.join(current_app.config['CUSTOMER_UPLOAD_FOLDER'], filename))

                query = f"UPDATE customer SET " \
                        f"firstname = ?, " \
                        f"lastname = ?, " \
                        f"status = ?, " \
                        f"image = ? " \
                        f"WHERE id = ?"
                params = (firstname, lastname, status, filename, cid)
            else:
                query = f"UPDATE customer SET " \
                        f"firstname = ?, " \
                        f"lastname = ?, " \
                        f"status = ? " \
                        f"WHERE id = ?"
                params = (firstname, lastname, status, cid)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/customer?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student details from student page to filter db and throw to detail page
@customers.route('/admin/detail_customer', methods=['GET', 'POST'])
def detail_customer():
    if request.method == 'POST':
        cid = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM customer WHERE id = ?"
        rows = execute_query(query, (cid,))

        return render_template('admin/customer/detail_customer.html', rows=rows, page=page)
    else:
        return redirect('/admin/customer')


# ** Student delete on db
@customers.route('/admin/delete_customer', methods=['POST'])
def delete_customer():
    if request.method == "POST":
        try:
            cid = request.form['id']
            page_id = request.form['page_id']
            image = request.form['image_upload']

            # Delete the old image file if it's not the default image
            # if image != 'default_img':
            image_path = os.path.join(current_app.config['CUSTOMER_UPLOAD_FOLDER'], image)
            if os.path.isfile(image_path):
                os.remove(image_path)

            query = f"DELETE FROM customer WHERE id = ?"
            execute_query(query, (cid,), is_insert=True)

            return redirect('/admin/customer?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"
