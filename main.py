from flask import Flask, render_template, url_for, request, redirect, jsonify, abort
from flask_sitemap import Sitemap
from datetime import datetime
from babel import numbers
from server import crud, gmail, trello_helper
from slugify import slugify
from jinja2 import Environment, BaseLoader
from datetime import datetime, timedelta
from inspect import cleandoc

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config['SITEMAP_URL_SCHEME'] = 'https'
sitemap = Sitemap(app=app)

@app.after_request
def add_header(response):
    response.cache_control.public = True
    response.cache_control.max_age = 31536000
    return response

@app.route('/')
def home():
    return render_template('home.html', home_images=crud.get_home_images(crud.transaction()), home_text=crud.get_home_text())

@sitemap.register_generator
def sitemap_home():
    yield 'home', {}

@app.route('/about')
def about():
    return render_template('about.html', about=crud.get_about())

@sitemap.register_generator
def sitemap_about():
    yield 'about', {}

@app.route('/contribute')
def contribute():
    contribute_products = crud.get_contribute_products(crud.transaction(), 667, request.args)
    number_of_products = len(contribute_products)
    donation_skus = crud.get_donation_skus()
    return render_template('contribute.html', support_text=crud.get_contribute_text(), contribute_products=contribute_products, number_of_products=number_of_products, donation_skus=donation_skus, shipping_sku=crud.get_shipping_sku())

@sitemap.register_generator
def sitemap_contribute():
    yield 'contribute', {}

@app.route('/refresh_contribute_products')
def refresh_contribute_products():
    crud.sync_contribute_products_to_stripe()
    return ('', 204)

@app.route('/artwork', strict_slashes=False)
def artwork_collection():
    artworks = crud.get_artwork_collection(crud.transaction(), 375, args=request.args)
    return render_template('artwork_collection.html', artworks=artworks)

@sitemap.register_generator
def sitemap_artwork_collection():
    yield 'artwork_collection', {}

@app.route('/artwork/<string:id>', defaults={'slug': None})
@app.route('/artwork/<string:id>/<slug>')
def artwork(slug, id):
    artwork = crud.get_artwork(crud.transaction(), id, 667)
    if artwork is None:
        abort(404)
    number_of_images = len(artwork['images'])
    canonical_url = url_for('artwork', slug=slugify_title(artwork["title"]), id=id, _external=True)
    return render_template('artwork.html', artwork=artwork, number_of_tiles=number_of_images, canonical_url=canonical_url)

@sitemap.register_generator
def sitemap_artwork():
    artworks = crud.get_artwork_collection(crud.transaction(), 375, args=None)
    for artwork in artworks:
        yield 'artwork', {'slug': slugify_title(artwork['title']), 'id': artwork['id']}

@app.route('/artwork-buy/<string:id>', methods=['POST'])
def artwork_buy(id):
    artwork = crud.get_artwork(crud.transaction(), id, 240)
    artwork_url = url_for('artwork', slug=slugify_title(artwork["title"]), id=id, _external=True)
    if artwork is None:
        abort(404)
    enquiry_email_template = crud.get_artwork_buy_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_address = f"{request.form.get('city')}, {request.form.get('country')}"
    enquirer_address_type = request.form.get('address_type')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Psyclonic Studios artwork enquiry: {artwork['title']}"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, address=enquirer_address, address_type=enquirer_address_type, artwork=artwork, message=enquirer_message, artwork_url=artwork_url)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_customer=True)
    email_response = gmail.send_email(email)

    trello_title = f'Buyer - {enquirer_name}'
    trello_description = cleandoc(f"""
    ## [Respond to the customer here]({gmail.get_email_link(email_response['id'])})
    ## Customer details
    Name: {enquirer_name}
    Email address: {enquirer_email_address}
    Address: {enquirer_address} ({enquirer_address_type})
    Artwork: [{artwork['title']}]({artwork_url})
    Message: {enquirer_message}
    """)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.BUYER_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

@app.route('/artwork-enquire/<string:id>', methods=['POST'])
def artwork_enquire(id):
    artwork = crud.get_artwork(crud.transaction(), id, 240)
    artwork_url = url_for('artwork', slug=slugify_title(artwork["title"]), id=id, _external=True)
    if artwork is None:
        abort(404)
    enquiry_email_template = crud.get_artwork_enquiry_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Psyclonic Studios artwork enquiry: {artwork['title']}"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, artwork=artwork, message=enquirer_message, artwork_url=artwork_url)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_customer=True)
    gmail.send_email(email)

    email_response = gmail.send_email(email)

    trello_title = f'Buyer - {enquirer_name}'
    trello_description = cleandoc(f"""
    ## [Respond to the customer here]({gmail.get_email_link(email_response['id'])})
    ## Customer details
    Name: {enquirer_name}
    Email address: {enquirer_email_address}
    Artwork: [{artwork['title']}]({artwork_url})
    Message: {enquirer_message}
    """)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

@app.route('/series', strict_slashes=False)
def series_collection():
    series_collection = crud.get_series_collection(crud.transaction(), 375, args=request.args)
    return render_template('series_collection.html', series_collection=series_collection)

@sitemap.register_generator
def sitemap_series_collection():
    yield 'series_collection', {}

@app.route('/series/<string:id>', defaults={'slug': None})
@app.route('/series/<string:id>/<slug>')
def series(slug, id):
    series = crud.get_series(crud.transaction(), id, 667)
    if series is None:
        abort(404)
    number_of_tiles = len(series['artworks'])
    canonical_url = url_for('series', slug=slugify_title(series["title"]), id=id, _external=True)
    return render_template('series.html', series=series, number_of_tiles=number_of_tiles, canonical_url=canonical_url)

@sitemap.register_generator
def sitemap_series():
    series_collection = crud.get_series_collection(crud.transaction(), 375, args=None)
    for series in series_collection:
        yield 'series', {'slug': slugify_title(series['title']), 'id': series['id']}

@app.route('/series-enquire/<string:id>', methods=['POST'])
def series_enquire(id):
    series = crud.get_series(crud.transaction(), id, 240)
    series_url = url_for('series', slug=slugify_title(series["title"]), id=id, _external=True)
    if series is None:
        abort(404)
    enquiry_email_template = crud.get_series_enquiry_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Psyclonic Studios series enquiry: {series['title']}"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, series=series, message=enquirer_message, series_url=series_url)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_customer=True)
    gmail.send_email(email)

    email_response = gmail.send_email(email)

    trello_title = f'Buyer - {enquirer_name}'
    trello_description = cleandoc(f"""
    ## [Respond to the customer here]({gmail.get_email_link(email_response['id'])})
    ## Customer details
    Name: {enquirer_name}
    Email address: {enquirer_email_address}
    Series: [{series['title']}]({series_url})
    Message: {enquirer_message}
    """)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

#@app.route('/blog', strict_slashes=False)
#def blog_collection():
#    blog_collection = crud.get_blog_collection(crud.transaction(), 375, args=request.args)
#    return render_template('blog_collection.html', blog_collection=blog_collection)

#@app.route('/workshop')
#def workshop_collection():
#    pass
#
#@app.route('/garage')
#def garage_collection():
#    pass

#@app.route('/blog/<string:id>')
#def blog(id):
#    blog = crud.get_blog(crud.transaction(), id, 667)
#    return render_template('blog.html', blog=blog)

@app.route('/legal',strict_slashes=False)
def legal():
    return render_template('legal.html', legal=crud.get_legal())

@sitemap.register_generator
def sitemap_legal():
    yield 'legal', {}

@app.route('/subscribe')
def subscribe():
    return render_template('subscribe.html', subscribe=crud.get_subscribe())

@sitemap.register_generator
def sitemap_subscribe():
    yield 'subscribe', {}

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.template_filter('format_money')
def format_money(money_str):
    return numbers.format_currency(money_str, 'AUD', locale='en_AU')

@app.template_filter('slugify')
def slugify_title(txt):
    return slugify(txt, max_length=25)

@app.context_processor
def inject_year():
    return {'this_year': datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
