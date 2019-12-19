from flask import Flask, render_template, url_for, request, redirect, jsonify, abort, session, make_response
from flask_sitemap import Sitemap
from datetime import datetime
from babel import numbers
from server import crud, gmail, trello_helper
from slugify import slugify
from jinja2 import Environment, BaseLoader
from datetime import datetime, timedelta
from inspect import cleandoc
import stripe
from server.secrets import SESSION_SECRET_KEY
from server.secrets import STRIPE_LIVE, STRIPE_TEST
import functools

STRIPE_DATA = STRIPE_TEST
stripe.api_key = STRIPE_DATA['key']

app = Flask(__name__)
app.secret_key = SESSION_SECRET_KEY
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

app.config['SITEMAP_URL_SCHEME'] = 'https'
sitemap = Sitemap(app=app)

def nocache(f):
    @functools.wraps(f)
    def nocache_route(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        return response
    return nocache_route

@app.route('/')
def home():
    return render_template('home.html', home_images=crud.get_home_images(crud.new_transaction()), home_text=crud.get_home_text())

@sitemap.register_generator
def sitemap_home():
    yield 'home', {}

@app.route('/about')
def about():
    return render_template('about.html', about=crud.get_about())

@sitemap.register_generator
def sitemap_about():
    yield 'about', {}

#@app.route('/contribute')
#def contribute():
#    contribute_products = crud.get_contribute_products(crud.new_transaction(), 667, request.args)
#    number_of_products = len(contribute_products)
#    donation_skus = crud.get_donation_skus()
#    return render_template('contribute.html', support_text=crud.get_contribute_text(), contribute_products=contribute_products, number_of_products=number_of_products, donation_skus=donation_skus, shipping_sku=crud.get_shipping_sku())
#
#@sitemap.register_generator
#def sitemap_contribute():
#    yield 'contribute', {}
#
#@app.route('/refresh_contribute_products')
#def refresh_contribute_products():
#    crud.sync_contribute_products_to_stripe()
#    return ('', 204)

@app.route('/artwork', strict_slashes=False)
def artwork_collection():
    artworks = crud.get_artwork_collection(crud.new_transaction(), 400, args=request.args)
    return render_template('artwork_collection.html', artworks=artworks)

@sitemap.register_generator
def sitemap_artwork_collection():
    yield 'artwork_collection', {}

@app.route('/artwork/<string:id>', defaults={'slug': None})
@app.route('/artwork/<string:id>/<slug>')
def artwork(slug, id):
    artwork = crud.get_artwork(crud.new_transaction(), id, 700)
    if artwork is None:
        abort(404)
    number_of_images = len(artwork['images'])
    canonical_url = url_for('artwork', slug=slugify_title(artwork["title"]), id=id, _external=True)
    in_cart = id in session.get('cart', [])
    return render_template('artwork.html', artwork=artwork, number_of_tiles=number_of_images, canonical_url=canonical_url, in_cart=in_cart)

@sitemap.register_generator
def sitemap_artwork():
    artworks = crud.get_artwork_collection(crud.new_transaction(), 400, args=None)
    for artwork in artworks:
        yield 'artwork', {'slug': slugify_title(artwork['title']), 'id': artwork['id']}

@app.route('/artwork-add-to-cart/', methods=['POST'])
def artwork_add_to_cart():
    artwork_id = request.form.get('artwork_id')
    if 'cart' not in session or type(session['cart']) is not dict:
        session['cart'] = {artwork_id: 1}
    else:
        cart = session['cart']
        cart[artwork_id] = 1
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/artwork-remove-from-cart/<string:id>')
def artwork_remove_from_cart(id):
    cart = session.get('cart', {})
    cart.pop(id, None)
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/artwork-buy/<string:id>', methods=['POST'])
def artwork_buy(id):
    artwork = crud.get_artwork(crud.new_transaction(), id, 240)
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
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_me='customer')
    email_response = gmail.send_email(email)

    trello_title = f'Buyer - {enquirer_name}'
    trello_description = render_template('trello_shipping_enquiry_description.md', gmail_link=gmail.get_email_link(email_response['id']), enquirer_name=enquirer_name, enquirer_email_address=enquirer_email_address, enquirer_address=enquirer_address, artwork=artwork, artwork_url=artwork_url, enquirer_message=enquirer_message)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ARTWORK_ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

@app.route('/artwork-enquire/<string:id>', methods=['POST'])
def artwork_enquire(id):
    artwork = crud.get_artwork(crud.new_transaction(), id, 240)
    artwork_url = url_for('artwork', slug=slugify_title(artwork["title"]), id=id, _external=True)
    if artwork is None:
        abort(404)
    enquiry_email_template = crud.get_artwork_enquiry_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Psyclonic Studios artwork enquiry: {artwork['title']}"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, artwork=artwork, message=enquirer_message, artwork_url=artwork_url)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_me='customer')
    email_response = gmail.send_email(email)

    trello_title = f'Buyer - {enquirer_name}'
    trello_description = render_template('trello_artwork_enquiry_description.md', gmail_link=gmail.get_email_link(email_response['id']), enquirer_name=enquirer_name, enquirer_email_address=enquirer_email_address, artwork=artwork, artwork_url=artwork_url, enquirer_message=enquirer_message)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

@app.route('/series', strict_slashes=False)
def series_collection():
    series_collection = crud.get_series_collection(crud.new_transaction(), 400, args=request.args)
    return render_template('series_collection.html', series_collection=series_collection)

@sitemap.register_generator
def sitemap_series_collection():
    yield 'series_collection', {}

@app.route('/series/<string:id>', defaults={'slug': None})
@app.route('/series/<string:id>/<slug>')
def series(slug, id):
    series = crud.get_series(crud.new_transaction(), id, 700)
    if series is None:
        abort(404)
    number_of_tiles = len(series['artworks'])
    canonical_url = url_for('series', slug=slugify_title(series["title"]), id=id, _external=True)
    return render_template('series.html', series=series, number_of_tiles=number_of_tiles, canonical_url=canonical_url)

@sitemap.register_generator
def sitemap_series():
    series_collection = crud.get_series_collection(crud.new_transaction(), 240, args=None)
    for series in series_collection:
        yield 'series', {'slug': slugify_title(series['title']), 'id': series['id']}

@app.route('/series-enquire/<string:id>', methods=['POST'])
def series_enquire(id):
    series = crud.get_series(crud.new_transaction(), id, 240)
    series_url = url_for('series', slug=slugify_title(series["title"]), id=id, _external=True)
    if series is None:
        abort(404)
    enquiry_email_template = crud.get_series_enquiry_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Psyclonic Studios series enquiry: {series['title']}"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, series=series, message=enquirer_message, series_url=series_url)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_me='customer')
    email_response = gmail.send_email(email)

    trello_title = f'Enquirer - {enquirer_name}'
    trello_description = render_template('trello_series_enquiry_description.md', gmail_link=gmail.get_email_link(email_response['id']), enquirer_name=enquirer_name, enquirer_email_address=enquirer_email_address, artwork=artwork, series_url=series_url, enquirer_message=enquirer_message)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ARTWORK_ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())

#@app.route('/blog', strict_slashes=False)
#def blog_collection():
#    blog_collection = crud.get_blog_collection(crud.new_transaction(), 375, args=request.args)
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
#    blog = crud.get_blog(crud.new_transaction(), id, 667)
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

@app.route('/contact')
def contact():
    return render_template('contact.html', contact_message=crud.get_contact_message())

@sitemap.register_generator
def sitemap_contact():
    yield 'contact', {}

@app.route('/contact', methods=['POST'])
def contact_send_email():
    enquiry_email_template = crud.get_contact_email_template()
    
    enquirer_email_address = request.form.get('email')
    enquirer_name = request.form.get('name')
    enquirer_message = request.form.get('message')
    
    email_subject = f"Contact Psyclonic Studios"
    email_body = Environment(loader=BaseLoader()).from_string(enquiry_email_template).render(name=enquirer_name, message=enquirer_message)
    email = gmail.compose_email_from_me(enquirer_email_address, email_subject, email_body, cc_me='contact')
    email_response = gmail.send_email(email)

    trello_title = f'Contact - {enquirer_name}'
    trello_description = render_template('trello_contact_description.md', gmail_link=gmail.get_email_link(email_response['id']), enquirer_name=enquirer_name, enquirer_email_address=enquirer_email_address, enquirer_message=enquirer_message)
    trello_due = datetime.today() + timedelta(3)
    trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ARTWORK_ENQUIRY_LABEL], position='top')
    return render_template('enquiry_success.html', thankyou_text=crud.get_enquire_thankyou())


@app.route('/payment_success', methods=['GET'])
@nocache
def payment_success():
    session.pop('cart', None)
    session.pop('payment_intent', None)
    return render_template('payment_success.html', thankyou_text=crud.get_payment_success())

@app.route('/cart')
@nocache
def cart():
    cart = session.get('cart', {})
    transaction = crud.new_transaction()
    cart_items = [{'artwork': crud.get_artwork(transaction, id, 240), 'quantity': cart[id]} for id in cart]
    cart_subtotal = sum(item['artwork']['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, cart_subtotal=cart_subtotal, hide_cart=True)

@app.route('/checkout', methods=['POST'])
@nocache
def checkout():
    shipping_country = request.form.get('country')
    shipping_cost = 0 if shipping_country.lower() == 'australia' else crud.get_international_shipping()

    cart = session.get('cart', {})
    transaction = crud.new_transaction()
    cart_items = [{'artwork': crud.get_artwork(transaction, id, 240), 'quantity': cart[id]} for id in cart]
    cart_subtotal = sum(item['artwork']['price'] * item['quantity'] for item in cart_items)

    total_cost = cart_subtotal + shipping_cost

    stripe_amount = int(total_cost * 100)
    if 'payment_intent' in session and session['payment_intent']:
        intent = stripe.PaymentIntent.modify(
            session['payment_intent'],
            amount=stripe_amount,
            description=describe_cart(cart_items)
        )
    else:
        intent = stripe.PaymentIntent.create(
            amount=stripe_amount,
            currency='aud',
            description=describe_cart(cart_items)
        )
    session['payment_intent'] = intent.id
    crud.update_order(intent.id, cart, cart_subtotal, shipping_cost, total_cost, False)
    return render_template('checkout.html', country=shipping_country, cart_items=cart_items, cart_subtotal=cart_subtotal, shipping_cost=shipping_cost, grand_total=total_cost, client_secret=intent.client_secret, hide_cart=True)

@app.route('/confirm_payment', methods=['POST'])
def confirm_payment():
    stripe_event = request.json
    event = None
    try:
        event = stripe.Event.construct_from(
            request.json, stripe.api_key
        )
    except ValueError as e:
        abort(400)

    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        crud.finalise_order(payment_intent)
        final_order = crud.get_order(payment_intent.id)

        order_confirmation_email_subject = "Your order from Psyclonic Studios"
        order_confirmation_email_body = render_template('order_confirmation_email.html',order=final_order)
        order_confirmation_email = gmail.compose_email_from_me(final_order['customer']['email'], order_confirmation_email_subject, order_confirmation_email_body, cc_me='orders')
        order_confirmation_email_response = gmail.send_email(order_confirmation_email)

        trello_title = f"Order - {final_order['customer']['name']}"
        gmail_link = gmail.get_email_link(order_confirmation_email_response['id'])
        trello_description = render_template('trello_order_description.md', order=final_order, gmail_link=gmail_link)
        trello_due = datetime.today() + timedelta(3)
        trello_helper.create_customer_card(trello_title, desc=trello_description, due=str(trello_due), labels=[trello_helper.ONLINE_ORDER_LABEL], position='top')
    else:
        abort(400)
    return '', 204

def describe_cart(cart_items):
    num_artworks = sum([item['quantity'] for item in cart_items if 'artwork' in item])
    return f'{num_artworks}✕Artwork'[0:22]

#def cart_metadata(cart_items):

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

jinja_string_env = Environment(loader=BaseLoader())
jinja_string_env.filters['slugify'] = slugify
jinja_string_env.filters['format_money'] = format_money
jinja_string_env.filters['format_date'] = format_date


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
