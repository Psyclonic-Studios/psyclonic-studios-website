from google.cloud import firestore
from google.cloud import storage
import os

db = firestore.Client()
content = db.collection('fl_content')

storage_client = storage.client.Client()
bucket = storage_client.get_bucket('psyclonic-studios-website.appspot.com')

transaction = db.transaction()
@firestore.transactional
def get_artwork_collection(transaction, size, args):
    artworks_query = content.where('_fl_meta_.schema', '==', 'artwork')
    artworks_query = sort_query(artworks_query, args)
    artworks = []
    for artwork_ref in artworks_query.stream(transaction=transaction):
        artwork = artwork_ref.to_dict()
        image_refs = artwork['images']
        image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
        artwork['image_urls'] = image_urls
        artworks.append(artwork)
    return artworks

@firestore.transactional
def get_artwork(transaction, id, size):
    artwork = content.document(id).get(transaction=transaction).to_dict()
    image_refs = artwork['images']
    image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
    artwork['image_urls'] = image_urls
    return artwork

@firestore.transactional
def get_series_collection(transaction, size, args):
    series_query = content.where('_fl_meta_.schema', '==', 'series')
    series_query = sort_query(series_query, args)
    series_collection = []
    for series_ref in series_query.stream(transaction=transaction):
        series = series_ref.to_dict()
        series_image_refs = series['seriesImages']
        if series_image_refs:
            series_image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in series_image_refs]
            series['thumbnail_image'] = get_file_url(get_image_size_path(series_image_refs[0].get(transaction=transaction).to_dict(), size))
        else:
            artwork = series['artworks'][0].get(transaction=transaction).to_dict()
            artwork_image = artwork['images'][0].get(transaction=transaction).to_dict()
            artwork_image_url = get_file_url(get_image_size_path(artwork_image, size))
            series['thumbnail_image'] = artwork_image_url
        series_collection.append(series)
    return series_collection

@firestore.transactional
def get_series(transaction, id, size):
    series = content.document(id).get(transaction=transaction).to_dict()
    # todo
    #series_image_refs = series['seriesImages']
    #series_image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
    artworks_resolved = []
    for artwork_ref in series['artworks']:
        artwork = artwork_ref.get(transaction=transaction).to_dict()
        image_refs = artwork['images']
        image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
        artwork['image_urls'] = image_urls
        artworks_resolved.append(artwork)
    series['artworks_resolved'] = artworks_resolved
    return series

@firestore.transactional
def get_blog_collection(transaction, size, args):
    blog_collection_query = content.where('_fl_meta_.schema', '==', 'posts').where('status', '==', 'published')
    blog_collection_query = sort_query(blog_collection_query, args)
    blog_collection = []
    for blog_ref in blog_collection_query.stream(transaction=transaction):
        blog = blog_ref.to_dict()
        blog_thumbnail_ref = blog['thumbnail'][0]
        blog_thumbnail = get_file_url(get_image_size_path(blog_thumbnail_ref.get(transaction=transaction).to_dict(), size))
        blog['thumbnail_image'] = blog_thumbnail
        blog_collection.append(blog)
    return blog_collection

@firestore.transactional
def get_blog(transcation, id, size):
    blog = content.document(id).get(transaction=transaction).to_dict()
    thumbnail_ref = blog['thumbnail'][0]
    blog['thumbnail_image'] = get_file_url(get_image_size_path(thumbnail_ref.get(transaction=transaction).to_dict(), size))
    return blog

@firestore.transactional
def get_home_images(transaction, size):
    home_images_query = content.where('_fl_meta_.schema', '==', 'websiteImages').where('position', '==', 'Home').limit(1)
    home_images = next(home_images_query.stream(transaction=transaction)).to_dict()
    image_refs = home_images['images']
    image_urls = [get_file_url(get_image_size_path(image.get(transaction=transaction).to_dict(), size)) for image in image_refs]
    home_images['image_urls'] = image_urls
    return home_images

def get_home_text():
    home_component_query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', 'Home').limit(1)
    home_component = next(home_component_query.stream()).to_dict()
    home = home_component['content']
    return home

def get_about():
    about_component_query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', 'About').limit(1)
    about_component = next(about_component_query.stream()).to_dict()
    about = about_component['content']
    return about

def get_legal():
    legal_component_query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', 'Legal').limit(1)
    legal_component = next(legal_component_query.stream()).to_dict()
    legal = legal_component['content']
    return legal

@firestore.transactional
def get_support_products(transaction, size, args):
    support_products_query = content.where('_fl_meta_.schema', '==', 'supportProducts').where('available', '==', True)
    support_products_query = sort_query(support_products_query, args)
    support_products = []
    for product_ref in support_products_query.stream(transaction=transaction):
        product = product_ref.to_dict()
        print(product)
        product_artwork_image_ref = product['artworkImage'][0]
        product_artwork_image_url = get_file_url(get_image_size_path(product_artwork_image_ref.get(transaction=transaction).to_dict(), size))
        product['artwork_image_url'] = product_artwork_image_url
        product_image_ref = product['productImage'][0]
        product_image_url = get_file_url(get_image_size_path(product_image_ref.get(transaction=transaction).to_dict(), size))
        product['product_image_url'] = product_image_url
        support_products.append(product)
    return support_products

def get_support_text():
    support_component_query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', 'Support').limit(1)
    support_component = next(support_component_query.stream()).to_dict()
    support = support_component['content']
    return support

def get_subscribe():
    subscribe_component_query = content.where('_fl_meta_.schema', '==', 'websiteComponents').where('component', '==', 'Subscribe').limit(1)
    subscribe_component = next(subscribe_component_query.stream()).to_dict()
    subscribe = subscribe_component['content']
    return subscribe
    
def post_email_address(email):
    subscribers = db.collection('subscribers')
    subscribers.document(email).set({'events':True,'newsletter': True}, merge=True)

def get_file_url(path):
    flamelink_path = 'flamelink/media'
    blob = bucket.blob(os.path.join(flamelink_path, path))
    return blob.public_url

def get_image_size_path(image_dict, size):
    filename = image_dict['file']
    sizes = image_dict['sizes']
    if size == 240:
        return os.path.join('sized', str(size), filename)
    else:
        for s in sizes:
            if s['width'] == size:
                return os.path.join('sized', str(s['path']), filename)
    return filename

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