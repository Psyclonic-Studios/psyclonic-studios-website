from flask import Flask, render_template, url_for
from datetime import datetime
from server import crud

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/artwork', strict_slashes=False)
def artwork_collection():
    artworks = crud.get_artwork_collection(crud.transaction, 375)
    return render_template('artwork_collection.html', artworks=artworks)

@app.route('/artwork/<string:id>')
def artwork(id):
    artwork = crud.get_artwork(crud.transaction, id, 667)
    number_of_images = len(artwork['image_urls'])
    return render_template('artwork.html', artwork=artwork, number_of_tiles=number_of_images)

@app.route('/series', strict_slashes=False)
def series_collection():
    series_collection = crud.get_series_collection(crud.transaction, 375)
    return render_template('series_collection.html', series_collection=series_collection)

@app.route('/series/<string:id>')
def series(id):
    series = crud.get_series(crud.transaction, id, 667)
    number_of_tiles = len(series['artworks'])
    return render_template('series.html', series=series, number_of_tiles=number_of_tiles)

@app.route('/blog', strict_slashes=False)
def blog_collection():
    posts = crud.get_posts()
    return render_template('posts.html', posts=posts)

@app.route('/blog/<string:id>')
def blog(id):
    post = crud.get_post(id)
    return render_template('post.html', post=post)

@app.template_filter('format_date')
def format_date(datetime_str):
    date = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
    return date.strftime('%Y %b')

@app.context_processor
def inject_year():
    return {'this_year': datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
