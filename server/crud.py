from google.cloud import firestore
from google.cloud import storage
import os

db = firestore.Client()
content = db.collection('fl_content')

storage_client = storage.client.Client()
bucket = storage_client.get_bucket('psyclonic-studios-website.appspot.com')

transaction = db.transaction()
@firestore.transactional
def get_artwork_collection(transaction, size):
    artworks_query = content.where('_fl_meta_.schema', '==', 'artwork')
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
def get_series_collection(transaction, size):
    series_query = content.where('_fl_meta_.schema', '==', 'series')
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

def get_posts():
    posts = content.where('_fl_meta_.schema', '==', 'posts').where('status', '==', 'published')
    return map(lambda post: post.to_dict(), posts.stream())

def get_post(id):
    post = content.document(id)
    return post.get().to_dict()

def get_file_url(path):
    flamelink_path = 'flamelink/media'
    blob = bucket.blob(os.path.join(flamelink_path, path))
    return blob.public_url

def get_image_size_path(image_dict, size):
    filename = image_dict['file']
    sizes = image_dict['sizes']
    print
    if size == 240:
        return os.path.join('sized', str(size), filename)
    else:
        for s in sizes:
            if s['width'] == size:
                return os.path.join('sized', str(s['path']), filename)
    return filename
