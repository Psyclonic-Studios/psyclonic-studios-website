from flask import Flask, render_template, url_for, request, redirect, jsonify
from datetime import datetime
from babel import numbers
from server import crud

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', home_images=crud.get_home_images(crud.TRANSACTION, 999)['image_urls'], home_text=crud.get_home_text())

@app.route('/about')
def about():
    return render_template('about.html', about=crud.get_about())

@app.route('/contribute')
def contribute():
    contribute_products = crud.get_contribute_products(crud.TRANSACTION, 667, request.args)
    number_of_products = len(contribute_products)
    donation_skus = crud.get_donation_skus()
    return render_template('contribute.html', support_text=crud.get_contribute_text(), contribute_products=contribute_products, number_of_products=number_of_products, donation_skus=donation_skus, shipping_sku=crud.get_shipping_sku())

@app.route('/refresh_contribute_products')
def refresh_contribute_products():
    crud.sync_contribute_products_to_stripe()
    return ('', 204)

@app.route('/artwork', strict_slashes=False)
def artwork_collection():
    artworks = crud.get_artwork_collection(crud.TRANSACTION, 375, args=request.args)
    return render_template('artwork_collection.html', artworks=artworks)

@app.route('/artwork/<string:id>')
def artwork(id):
    artwork = crud.get_artwork(crud.TRANSACTION, id, 667)
    number_of_images = len(artwork['image_urls'])
    return render_template('artwork.html', artwork=artwork, number_of_tiles=number_of_images)

@app.route('/series', strict_slashes=False)
def series_collection():
    series_collection = crud.get_series_collection(crud.TRANSACTION, 375, args=request.args)
    return render_template('series_collection.html', series_collection=series_collection)

@app.route('/series/<string:id>')
def series(id):
    series = crud.get_series(crud.TRANSACTION, id, 667)
    number_of_tiles = len(series['artworks'])
    return render_template('series.html', series=series, number_of_tiles=number_of_tiles)

#@app.route('/blog', strict_slashes=False)
#def blog_collection():
#    blog_collection = crud.get_blog_collection(crud.TRANSACTION, 375, args=request.args)
#    return render_template('blog_collection.html', blog_collection=blog_collection)

#@app.route('/workshop')
#def workshop_collection():
#    pass
#
#@app.route('/garage')
#def garage_collection():
#    pass

@app.route('/blog/<string:id>')
def blog(id):
    blog = crud.get_blog(crud.TRANSACTION, id, 667)
    return render_template('blog.html', blog=blog)

@app.route('/legal',strict_slashes=False)
def legal():
    return render_template('legal.html', legal=crud.get_legal())

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html', subscribe=crud.get_subscribe())

@app.route('/subscribe',methods=['POST'])
def add_subscriber():
    email = request.form.get('email')
    crud.post_email_address(email)
    return render_template('subscribe_success.html', thankyou_text=crud.get_subscribe_success())

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html', thankyou_text=crud.get_payment_success())

@app.template_filter('format_date')
def format_date(datetime_str):
    date = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
    return date.strftime('%Y %b')

@app.template_filter('format_money')
def format_money(money_str):
    return numbers.format_currency(money_str, 'AUD', locale='en_AU')

@app.context_processor
def inject_year():
    return {'this_year': datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
