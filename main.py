from flask import Flask, render_template, url_for, request
from datetime import datetime
from server import crud

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html', home_images=crud.get_home_images(crud.transaction, 999)['image_urls'])

@app.route('/about')
def about():
    return render_template('about.html', about=crud.get_about())

@app.route('/artwork', strict_slashes=False)
def artwork_collection():
    artworks = crud.get_artwork_collection(crud.transaction, 375, args=request.args)
    return render_template('artwork_collection.html', artworks=artworks)

@app.route('/artwork/<string:id>')
def artwork(id):
    artwork = crud.get_artwork(crud.transaction, id, 667)
    number_of_images = len(artwork['image_urls'])
    return render_template('artwork.html', artwork=artwork, number_of_tiles=number_of_images)

@app.route('/series', strict_slashes=False)
def series_collection():
    series_collection = crud.get_series_collection(crud.transaction, 375, args=request.args)
    return render_template('series_collection.html', series_collection=series_collection)

@app.route('/series/<string:id>')
def series(id):
    series = crud.get_series(crud.transaction, id, 667)
    number_of_tiles = len(series['artworks'])
    return render_template('series.html', series=series, number_of_tiles=number_of_tiles)

#@app.route('/blog', strict_slashes=False)
#def blog_collection():
#    blog_collection = crud.get_blog_collection(crud.transaction, 375, args=request.args)
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
    blog = crud.get_blog(crud.transaction, id, 667)
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
    return render_template('subscribe_success.html')

@app.template_filter('format_date')
def format_date(datetime_str):
    date = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S%z')
    return date.strftime('%Y %b')

@app.context_processor
def inject_year():
    return {'this_year': datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
