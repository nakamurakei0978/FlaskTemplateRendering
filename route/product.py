from datetime import datetime
from unicodedata import decimal

from flask import Blueprint, render_template, request, redirect, current_app
from werkzeug.utils import secure_filename
import os
from config import execute_query

products = Blueprint('products', __name__)


# ** filter db and get all data and throw to student list page
@products.route('/admin/product')
def product():
    # Get the page number from the query parameters (default to 1 if not present)
    page = request.args.get('page', 1, type=int)

    # Define the number of records per page
    records_per_page = 7

    # Calculate the offset based on the current page
    offset = (page - 1) * records_per_page

    # Use the helper function to execute the query
    rows = execute_query("SELECT *, (select cname from product_category where product.category_id = cid) as cname "
                         "FROM product LIMIT ? OFFSET ?",
                         (records_per_page, offset))

    # Calculate the total number of pages
    total_records = execute_query("SELECT COUNT(*) FROM product")[0][0]
    total_pages = (total_records // records_per_page) + (total_records % records_per_page > 0)

    return render_template('admin/product/index.html', rows=rows, page=page, total_pages=total_pages)


# ** load to add student page
@products.route('/admin/add_product')
def add_product():
    categories = execute_query("SELECT * FROM product_category")
    return render_template('admin/product/add_product.html', categories=categories)


# ** student added to db
@products.route('/admin/product_added', methods=['POST'])
def product_added():
    if request.method == "POST":
        try:
            pname = request.form['productName']
            category_id = request.form['category']
            cost = round(float(request.form['cost']), 2) * 100
            price = round(float(request.form['price']), 2) * 100
            qty = request.form['qty']
            desc = request.form['description']
            created_date = datetime.now().strftime("%d-%m-%y")

            if category_id == 'Select category':
                cname = ''

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
                filename = secure_filename(f"{pname}_{cost+price}{extension}")
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                query = "INSERT INTO product (name,category_id,description," \
                        "qty, cost_in_cent,price_in_cent,image, created_date) VALUES (?,?,?,?,?,?,?,?)"
                params = (pname, category_id, desc, qty, cost, price, filename, created_date)
            else:
                query = "INSERT INTO product (name,category_id,description," \
                        "qty, cost_in_cent,price_in_cent, created_date) VALUES (?,?,?,?,?,?,?)"
                params = (pname, category_id, desc, qty, cost, price, created_date)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/product')
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student detail from student page or detail page to filter db and throw to edit page
@products.route('/admin/edit_product', methods=['GET', 'POST'])
def edit_product():
    if request.method == 'POST':
        product_id = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM product WHERE id = ?"
        rows = execute_query(query, (product_id,))
        categories = execute_query("SELECT * FROM product_category")

        return render_template('admin/product/edit_product.html', rows=rows, page=page, categories=categories)
    else:
        return redirect('/admin/product')


# ** Student edit or update to db
@products.route('/admin/product_edited', methods=['POST'])
def product_edited():
    if request.method == "POST":
        try:
            pid = request.form['id']
            page_id = request.form['page_id']
            name = request.form['productName']
            desc = request.form['description']
            category_id = request.form['category']
            cost = round(float(request.form['cost']), 2) * 100
            price = round(float(request.form['price']), 2) * 100
            qty = request.form['qty']

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
                old_image_query = "SELECT image FROM product WHERE id = ?"
                old_image_filename = execute_query(old_image_query, (pid,), is_insert=False)[0]['image']

                # Delete the old image file
                if old_image_filename:
                    old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_image_filename)
                    if os.path.isfile(old_image_path):
                        os.remove(old_image_path)

                # Save the image to the uploads folder, with fisrtname_lastname.extension as the filename
                filename = secure_filename(f"{name}_{cost+price}{extension}")
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

                query = f"UPDATE product SET " \
                        f"name = ?, " \
                        f"category_id = ?, " \
                        f"description = ?, " \
                        f"qty = ?, " \
                        f"cost_in_cent = ?, " \
                        f"price_in_cent = ?, " \
                        f"image = ? " \
                        f"WHERE id = ?"
                params = (name, category_id, desc, qty, cost, price, filename, pid)
            else:
                query = f"UPDATE product SET " \
                        f"name = ?, " \
                        f"category_id = ?, " \
                        f"description = ?, " \
                        f"qty = ?, " \
                        f"cost_in_cent = ?, " \
                        f"price_in_cent = ? " \
                        f"WHERE id = ?"
                params = (name, category_id, desc, qty, cost, price, pid)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/product?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student details from student page to filter db and throw to detail page
@products.route('/admin/detail_product', methods=['GET', 'POST'])
def detail_product():
    if request.method == 'POST':
        product_id = request.form.get("id", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT *, (select cname from product_category where cid==product.category_id) cname " \
                f"FROM product WHERE id = ?"
        rows = execute_query(query, (product_id,))

        return render_template('admin/product/detail_product.html', rows=rows, page=page)
    else:
        return redirect('/admin/product')


# ** Student delete on db
@products.route('/admin/delete_product', methods=['POST'])
def delete_product():
    if request.method == "POST":
        try:
            pid = request.form['id']
            page_id = request.form['page_id']
            image = request.form['image_upload']

            # Delete the old image file if it's not the default image
            if image != 'default_img':
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image)
                if os.path.isfile(image_path):
                    os.remove(image_path)

            query = f"DELETE FROM product WHERE id = ?"
            execute_query(query, (pid,), is_insert=True)

            return redirect('/admin/product?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"
