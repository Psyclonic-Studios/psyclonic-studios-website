from google.cloud import firestore, storage, exceptions
import os

db = firestore.Client()
content = db.collection('fl_content')

storage_client = storage.client.Client()
bucket = storage_client.get_bucket('psyclonic-studios-website.appspot.com')

def new_transaction():
    return db.transaction()

@firestore.transactional
def get_artwork_collection(transaction, size, args):
    artworks_query = content.where('_fl_meta_.schema', '==', 'artwork')
    artworks_query = sort_query(artworks_query, args)
    artworks = []
    for artwork_ref in artworks_query.stream(transaction=transaction):
        artwork = artwork_ref.to_dict()
        image_refs = artwork['images']
        artwork['images'] = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in artwork['images']]
        artworks.append(artwork)
    return artworks

@firestore.transactional
def get_artwork(transaction, id, size):
    artwork = content.document(id).get(transaction=transaction).to_dict()
    if not artwork:
        return None
    artwork['images'] = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in artwork['images']]
    return artwork

@firestore.transactional
def get_artwork_from_ref(transaction, ref, size):
    artwork = ref.get(transaction=transaction).to_dict()
    if not artwork:
        return None
    artwork['images'] = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in artwork['images']]
    return artwork

@firestore.transactional
def get_non_series_artwork_collection(transaction, size, args):
    artworks_query = content.where('_fl_meta_.schema', '==', 'artwork').where('partOfASeries', '==', False)
    artworks_query = sort_query(artworks_query, args)
    artworks = []
    for artwork_ref in artworks_query.stream(transaction=transaction):
        artwork = artwork_ref.to_dict()
        image_refs = artwork['images']
        artwork['images'] = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in artwork['images']]
        artworks.append(artwork)
    return artworks

@firestore.transactional
def get_series_collection(transaction, size, args):
    series_query = content.where('_fl_meta_.schema', '==', 'series')
    series_query = sort_query(series_query, args)
    series_collection = []
    for series_ref in series_query.stream(transaction=transaction):
        series = series_ref.to_dict()
        series_image_refs = series['seriesImages']
        if series_image_refs:
            series_image_urls = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in series_image_refs]
            series['thumbnail_image'] = get_sized_image_urls(series_image_refs[0].get(transaction=transaction).to_dict(), size)
        else:
            artwork = series['artworks'][0].get(transaction=transaction).to_dict()
            artwork_image = artwork['images'][0].get(transaction=transaction).to_dict()
            artwork_image_url = get_sized_image_urls(artwork_image, size)
            series['thumbnail_image'] = artwork_image_url
        series_collection.append(series)
    return series_collection

@firestore.transactional
def get_series(transaction, id, size):
    series = content.document(id).get(transaction=transaction).to_dict()
    # todo
    #series_image_refs = series['seriesImages']
    #series_image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
    if not series:
        return None
    artworks_resolved = []
    for artwork_ref in series['artworks']:
        artwork = artwork_ref.get(transaction=transaction).to_dict()
        image_refs = artwork['images']
        image_urls = [get_sized_image_urls(image.get(transaction=transaction).to_dict(), size) for image in image_refs]
        artwork['images'] = image_urls
        artworks_resolved.append(artwork)
    series['artworks_resolved'] = artworks_resolved
    return series

#
#@firestore.transactional
#def get_blog_collection(transaction, size, args):
#    blog_collection_query = content.where('_fl_meta_.schema', '==', 'posts').where('status', '==', 'published')
#    blog_collection_query = sort_query(blog_collection_query, args)
#    blog_collection = []
#    for blog_ref in blog_collection_query.stream(transaction=transaction):
#        blog = blog_ref.to_dict()
#        blog_thumbnail_ref = blog['thumbnail'][0]
#        blog_thumbnail = get_file_url(get_image_size_path(blog_thumbnail_ref.get(transaction=transaction).to_dict(), size))
#        blog['thumbnail_image'] = blog_thumbnail
#        blog_collection.append(blog)
#    return blog_collection
#
#@firestore.transactional
#def get_blog(transaction, id, size):
#    blog = content.document(id).get(transaction=transaction).to_dict()
#    thumbnail_ref = blog['thumbnail'][0]
#    blog['thumbnail_image'] = get_file_url(get_image_size_path(thumbnail_ref.get(transaction=transaction).to_dict(), size))
#    return blog

@firestore.transactional
def get_home_images(transaction):
    home_images_query = content.where('_fl_meta_.schema', '==', 'websiteImages').where('position', '==', 'Home').limit(1)
    home_images = next(home_images_query.stream(transaction=transaction)).to_dict()
    home_images['images'] = [get_sized_image_urls(image.get(transaction=transaction).to_dict()) for image in home_images['images']]
    return home_images

def get_cost(cost):
    query = content.where('_fl_meta_.schema', '==', 'costs').where('name', '==', cost).limit(1)
    cost = next(query.stream()).to_dict()
    return cost['cost']

def get_international_shipping():
    return get_cost('International shipping')

def get_website_component(component):
    query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', component).limit(1)
    component = next(query.stream()).to_dict()
    return component['content']

def get_home_text():
    return get_website_component('Home')

def get_about():
    return get_website_component('About')

def get_legal():
    return get_website_component('Legal')

@firestore.transactional
def get_contribute_products(transaction, size, args):
    contribute_products_query = content.where('_fl_meta_.schema', '==', 'supportProducts').where('available', '==', True)
    contribute_products_query = sort_query(contribute_products_query, args)
    contribute_products = []
    for product_ref in contribute_products_query.stream(transaction=transaction):
        product = product_ref.to_dict()
        product['sku'] = f'sku_{product["id"]}'
        product_artwork_image_ref = product['artworkImage'][0]
        product['artwork_image'] = get_sized_image_urls(product_artwork_image_ref.get(transaction=transaction).to_dict(), size)
        product_image_ref = product['productImage'][0]
        product['product_image'] = get_sized_image_urls(product_image_ref.get(transaction=transaction).to_dict(), size)
        contribute_products.append(product)
    return contribute_products

#def sync_contribute_products_to_stripe():
#    contribution_product_id = STRIPE_DATA['contribution_product_id']
#    contribute_products = get_contribute_products(new_transaction(), 375, None)
#    products = {product['sku']: product for product in contribute_products}
#    stripe_skus = stripe.SKU.list(product=contribution_product_id, limit=100)['data']
#    stripe_sku_list = [sku['id'] for sku in stripe_skus]
#    existing_skus = filter(lambda sku: sku in stripe_sku_list, products.keys())
#    new_skus = filter(lambda sku: sku not in stripe_sku_list, products.keys())
#    
#    for sku in existing_skus:
#        product = products[sku]
#        stripe.SKU.modify(
#            sku,
#            currency='aud',
#            inventory={'type': 'infinite'},
#            active=product['available'],
#            price=int(product['basePrice'] * 100),
#            image=product['product_image_url'],
#            product=contribution_product_id,
#            attributes={'name': product['title']}
#        )
#
#    for sku in new_skus:
#        product = products[sku]
#        stripe.SKU.create(
#            id=product['sku'],
#            currency='aud',
#            inventory={'type': 'infinite'},
#            active=product['available'],
#            price=int(product['basePrice'] * 100),
#            image=product['product_image_url'],
#            product=contribution_product_id,
#            attributes={'name': product['title']}
#        )
#    
#def get_donation_skus():
#    donation_product_id = STRIPE_DATA['donation_product_id']
#    donation_skus = stripe.SKU.list(product=donation_product_id)['data']
#    return sorted(donation_skus, key=lambda sku: sku['price'])
#
#def get_shipping_sku():
#    shipping_sku = stripe.SKU.retrieve(STRIPE_DATA['shipping_sku_id'])
#    return shipping_sku

def get_contribute_text():
    return get_website_component('Contribute')

def get_subscribe():
    return get_website_component('Subscribe')
    
def get_contact_message():
    return get_website_component('Contact message')

def get_contact_email_template():
    return get_website_component('Contact email template')

def get_subscribe_success():
    return get_website_component('Thankyou subscribe')

def post_email_address(email):
    subscribers = db.collection('subscribers')
    subscribers.document(email).set({'subscribe': True}, merge=True)

def get_artwork_buy_email_template():
    return get_website_component('Artwork buy email')

def get_artwork_enquiry_email_template():
    return get_website_component('Artwork enquire email')

def get_series_enquiry_email_template():
    return get_website_component('Series enquire email')

def get_enquire_thankyou():
    return get_website_component('Thankyou enquiry')

def get_payment_success():
    return get_website_component('Thankyou payment')

def get_order(id):
    order = db.collection('orders').document(id).get().to_dict()
    transaction = new_transaction()
    artworks = [{'artwork': get_artwork_from_ref(transaction, artwork['artwork'], 300), 'quantity': artwork['quantity']} for artwork in  order['artworks']]
    order['artworks'] = artworks
    return order

def finalise_order(payment_intent):
    orders = db.collection('orders')
    order = orders.document(payment_intent.id)
    order.update({
        'payment_recieved': True,
        'customer': {
            'name': payment_intent.shipping.name,
            'email': payment_intent.receipt_email
        },
        'shipping': {
            'street': payment_intent.shipping.address.line1,
            'city': payment_intent.shipping.address.city,
            'state': payment_intent.shipping.address.state,
            'country': payment_intent.shipping.address.country,
            'postal_code': payment_intent.shipping.address.postal_code,
        },
        'paid_at': firestore.SERVER_TIMESTAMP
    })

    artworks = order.get().to_dict()['artworks']
    for artwork in artworks:
        artwork['artwork'].update({'inventory': firestore.Increment(-artwork['quantity'])})

def update_order(payment_intent_id, cart, subtotal, shipping_cost, total, payment_recieved):
    orders = db.collection('orders')
    order = orders.document(payment_intent_id)
    #try:
    #    order_doc = order.get()
    #    if 'created_at' not in order_doc.to_dict():
    #        order.update({'created_at': firestore.SERVER_TIMESTAMP})
    #except exceptions.NotFound:
    #    order.set({'created_at': firestore.SERVER_TIMESTAMP}, merge=True)
    artworks = [{'artwork': content.document(id), 'quantity': cart[id]} for id in cart]
    order_update = {'payment_recieved': False, 'artworks': artworks, 'cost': {'subtotal': subtotal, 'shipping': shipping_cost, 'total': total}}
    #order.update(order_update)
    order.set(order_update)

def get_flamelink_file_url(path):
    flamelink_path = 'flamelink/media'
    blob = bucket.blob(os.path.join(flamelink_path, path))
    return blob.public_url

def get_sized_image_urls(image_dict, upto=None):
    filename = image_dict['file']
    image_dict['full_size'] = {'width': 'full', 'storage_path': filename, 'url': get_flamelink_file_url(filename)}
    sizes = image_dict['sizes']
    if upto:
        sizes = list(filter(lambda size: size['width'] <= upto, sizes))
    for s in sizes:
        s['storage_path'] = os.path.join('sized', str(s['path']), filename)
    sizes = {s['width']: s for s in sizes}
    sizes[240] = {'width': 240, 'storage_path': os.path.join('sized', str(240), filename)}
    for size in sizes.values():
        size['url'] = get_flamelink_file_url(size['storage_path'])
    image_dict['full_size'] = sizes[max(sizes)]
    image_dict['sizes'] = sizes
    return image_dict

def sort_query(query, args=None):
    if args is None:
        return query
    sort_by = args.get('sort_by','')
    sort_direction = args.get('sort_direction','')
    if sort_by:
        if sort_direction == 'descending':
            query = query.order_by(sort_by, direction=firestore.Query.DESCENDING)
        elif sort_direction == 'ascending':
            query = query.order_by(sort_by, direction=firestore.Query.ASCENDING)
        else:
            query = query.order_by(sort_by)
    return query