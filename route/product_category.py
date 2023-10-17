from datetime import datetime
from unicodedata import decimal

from flask import Blueprint, render_template, request, redirect, current_app
from werkzeug.utils import secure_filename
import os
from config import execute_query

product_categories = Blueprint('product_categories', __name__)


# ** filter db and get all data and throw to student list page
@product_categories.route('/admin/category')
def category():
    # Get the page number from the query parameters (default to 1 if not present)
    page = request.args.get('page', 1, type=int)

    # Define the number of records per page
    records_per_page = 7

    # Calculate the offset based on the current page
    offset = (page - 1) * records_per_page

    # Use the helper function to execute the query
    rows = execute_query("SELECT * FROM product_category LIMIT ? OFFSET ?",
                         (records_per_page, offset))

    # Calculate the total number of pages
    total_records = execute_query("SELECT COUNT(*) FROM product_category")[0][0]
    total_pages = (total_records // records_per_page) + (total_records % records_per_page > 0)

    return render_template('admin/product_category/index.html', rows=rows, page=page, total_pages=total_pages)


# ** load to add student page
@product_categories.route('/admin/add_category')
def add_category():
    return render_template('admin/product_category/add_category.html')


# ** student added to db
@product_categories.route('/admin/category_added', methods=['POST'])
def category_added():
    if request.method == "POST":
        try:
            cname = request.form['cname']
            desc = request.form['desc']

            query = "INSERT INTO product_category (cname,cdescription) VALUES (?,?)"
            params = (cname, desc)

            execute_query(query, params, is_insert=True)

            return redirect('/admin/category')
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student detail from student page or detail page to filter db and throw to edit page
@product_categories.route('/admin/edit_category', methods=['GET', 'POST'])
def edit_category():
    if request.method == 'POST':
        cid = request.form.get("cid", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM product_category WHERE cid = ?"
        rows = execute_query(query, (cid,))

        return render_template('admin/product_category/edit_category.html', rows=rows, page=page)
    else:
        return redirect('/admin/category')


# ** Student edit or update to db
@product_categories.route('/admin/category_edited', methods=['POST'])
def category_edited():
    if request.method == "POST":
        try:
            cid = request.form['cid']
            page_id = request.form['page_id']
            cname = request.form['cname']
            desc = request.form['desc']

            query = f"UPDATE product_category SET " \
                    f"cname = ?, " \
                    f"cdescription = ? " \
                    f"WHERE cid = ?"
            params = (cname, desc, (cid,))

            execute_query(query, params, is_insert=True)

            return redirect('/admin/category?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"


# ** get student details from student page to filter db and throw to detail page
@product_categories.route('/admin/detail_category', methods=['GET', 'POST'])
def detail_category():
    if request.method == 'POST':
        cid = request.form.get("cid", None)
        page = request.form['page_id']

        # ** student_sid pass as parameter to prevent sql injection
        query = f"SELECT * FROM product_category WHERE cid = ?"
        rows = execute_query(query, (cid,))

        return render_template('admin/product_category/detail_category.html', rows=rows, page=page)
    else:
        return redirect('/admin/category')


# ** Student delete on db
@product_categories.route('/admin/delete_category', methods=['POST'])
def delete_category():
    if request.method == "POST":
        try:
            cid = request.form['cid']
            page_id = request.form['page_id']

            query = f"DELETE FROM product_category WHERE cid = ?"
            execute_query(query, (cid,), is_insert=True)

            return redirect('/admin/category?page=' + page_id)
        except Exception as e:
            return f"An error occurred: {str(e)}"
