import random
import lorem as lorem
import randomname
from flask import Flask, render_template, request

from route.student import students
from route.product import products
from route.product_category import product_categories
from route.customer import customers
from route.user import users
from route.currency import currencies

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/image/student'
app.config['UPLOAD_FOLDER'] = 'static/image/product'
app.config['UPLOAD_FOLDER'] = 'static/image/customer'
app.config['UPLOAD_FOLDER'] = 'static/image/user'

app.register_blueprint(students)
app.register_blueprint(products)
app.register_blueprint(product_categories)
app.register_blueprint(customers)
app.register_blueprint(users)
app.register_blueprint(currencies)

products = [
    {
        'id': 1,
        'name': 'coca',
        'price': 10,
        'discount': 50,
        'category': 'drink',
        'rating': 4.8,
    },
]
categories = [
    {
        'id': 1,
        'name': 'drink',
    },
    {
        'id': 2,
        'name': 'icecream',
    },
    {
        'id': 3,
        'name': 'Food',
    },
    {
        'id': 4,
        'name': 'Fast Food',
    },
    {
        'id': 5,
        'name': 'Wine',
    },
    {
        'id': 6,
        'name': 'Cafe',
    }
]
for item in range(12):
    category = random.choice(categories)
    products.append({
        'id': 1,
        'name': randomname.get_name(noun='food'),
        'price': random.randrange(1, 101, 2),
        'discount': random.randrange(10, 51),
        'category': category['name'],
        'rating': random.randrange(0, 51)
    })


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error/404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error/500.html"), 500


@app.route('/dashboard')
@app.route("/admin")
def admin():
    return render_template("admin/dashboard/index.html")


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    filter_category = request.args.get('filter_category', default='all', type=str)

    product_filtered = []
    if filter_category == 'all':
        product_filtered = products
    else:
        for product_found in products:
            if product_found['category'] == filter_category:
                product_filtered.append(product_found)

    return render_template("index.html", products=product_filtered, categories=categories,
                           filter_category=filter_category)


@app.route("/product_detail/<string:name>/<string:price>/<string:discount>/<string:category>/<string:rating>/<string"
           ":image>")
def product_detail(name, price, discount, category, rating, image):
    description = lorem.paragraph()
    return render_template('component/product_detail.html', name=name, price=price, discount=discount,
                           category=category, rating=rating, image=image, description=description)



if __name__ == "__main__":
    app.run(debug=True)
