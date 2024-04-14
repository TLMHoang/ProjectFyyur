#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from datetime import timedelta
import json
import random
import dateutil.parser
import babel
import re
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import and_, func
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    is_talent = db.Column(db.Boolean, nullable=False, default=False)

    # Relationship
    shows = db.relationship('Show', backref='venue', uselist=False, lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    is_talent = db.Column(db.Boolean, nullable=False, default=False)
    
    # Relationship
    shows = db.relationship('Show', backref='artist', uselist=False, lazy=True)

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    #Relationship
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
#Seed
#----------------------------------------------------------------------------#
def seed_data():
    # Create venues
    venue1 = Venue(name='Quan 1', city='Ho Chi Minh', state='AL', address='Quan 1 - Ho Chi Minh', phone='000-000-0000')
    venue2 = Venue(name='Quan 2', city='Ho Chi Minh', state='AL', address='Quan 2 - Ho Chi Minh', phone='000-000-0000')
    venue3 = Venue(name='Quan 3', city='Ho Chi Minh', state='AL', address='Quan 3 - Ho Chi Minh', phone='000-000-0000')
    venue4 = Venue(name='Cau Giay', city='Ha Noi', state='AZ', address='Cau Giay - Ha Noi', phone='000-000-0000')
    venue5 = Venue(name='Long Bien', city='Ha Noi', state='AZ', address='Long Bien - Ha Noi', phone='000-000-0000')
    venue6 = Venue(name='Cau Rong', city='Da Nang', state='AK', address='Cau Rong - Da Nang', phone='000-000-0000')

    # Create artists
    artist1 = Artist(name='Ca si A', city='Ho Chi Minh', state='AL', phone='000-000-0000')
    artist2 = Artist(name='Ca si B', city='Ha Noi', state='AZ', phone='000-000-0000')
    artist3 = Artist(name='Ca si C', city='Da Nang', state='AK', phone='000-000-0000')
    artist4 = Artist(name='Ca si D', city='Ho Chi Minh', state='AL', phone='000-000-0000')
    artist5 = Artist(name='Ca si E', city='Da Nang', state='AK', phone='000-000-0000')
    artist6 = Artist(name='Ca si F', city='Ha Noi', state='AZ', phone='000-000-0000')

    # Add venues and artists to session
    db.session.add_all([venue1, venue2, venue3, venue4, venue5, venue6, artist1, artist2, artist3, artist4, artist5, artist6])
    db.session.commit()

    # Generate shows for each artist
    artists = [artist1, artist2, artist3, artist4, artist5, artist6]
    venues = [venue1, venue2, venue3, venue4, venue5, venue6]

    for artist in artists:
        # Select random venues for the artist's shows
        artist_venues = random.sample(venues, 4)
        
        for venue in artist_venues:
            # Generate show times
            start_time = datetime.utcnow() + timedelta(days=random.randint(1, 30), hours=random.randint(1, 23), minutes=random.randint(0, 59))
            
            # Create show
            show = Show(start_time=start_time, venue=venue, artist=artist)
            db.session.add(show)

    # Commit all changes
    db.session.commit()

#----------------------------------------------------------------------------#
#function helper
#----------------------------------------------------------------------------#
def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return None

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  # seed_data()
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  group_venues = db.session.query(Venue.state, Venue.city).group_by(Venue.state, Venue.city).all()

  areas = []

  for item in group_venues:
    db_venues = db.session.query(
      Venue.id,
      Venue.name,
      func.count(Show.id)
      ).outerjoin(Show).filter(Venue.state == item[0], Venue.city == item[1]).group_by(Venue.id).all()
    venues = []
    for db_venue in db_venues:
       venues.append({
          "id": db_venue[0],
          "name": db_venue[1],
          "num_upcoming_shows": db_venue[2],
       })

    areas.append({
       "city": item[1],
       "state": item[0],
       "venues": venues
    })
  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  

  token = request.form.get('search_term', '')
  db_venues = db.session.query(
      Venue.id,
      Venue.name,
      func.count(Show.id)
      ).outerjoin(Show).filter(and_(Venue.name.like(f'%{token}%'))).group_by(Venue.id).all()
  venues = []
  for db_venue in db_venues:
    venues.append({
      "id": db_venue[0],
      "name": db_venue[1],
      "num_upcoming_shows": db_venue[2],
    })
  response={
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is None : return

  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time <= datetime.utcnow()).all()
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).all()
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.is_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  venue = Venue()

  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.address = request.form['address']
  venue.phone = request.form['phone']
  venue.image_link = request.form['image_link']
  venue.facebook_link = request.form['facebook_link']
  venue.genres = request.form['genres']
  venue.website_link = request.form['website_link']
  venue.seeking_description = request.form['seeking_description']
  venue.is_talent = False if request.form.get('seeking_talent') is None else True

  regex = r"""\d{3}-\d{3}-\d{4}"""
  if not re.search(regex, venue.phone):
    flash('Phone invalid')
    return render_template('pages/home.html')
  
  try:
    db.session.add(venue)
    db.session.commit()
  except Exception as e:
    flash('An error occurred. Venue ' + venue.name + ' could not be listed. \n Error: ' + e)
  finally:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is not None:
      try:
          db.session.delete(venue)
          db.session.commit()
          return None
      except Exception as e:
          db.session.rollback()
          return jsonify({'message': f'Error deleting venue: {str(e)}'}), 500
  else:
      return jsonify({'message': 'Venue not found'}), 404

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = db.session.query(Artist.id, Artist.name).all()
  data = []
  for artist in artists:
    data.append({
    "id": artist[0],
    "name": artist[1],
  })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  token = request.form.get('search_term', '')
  db_artists = db.session.query(
      Artist.id,
      Artist.name,
      func.count(Show.id)
      ).outerjoin(Show).filter(and_(Artist.name.like(f'%{token}%'))).group_by(Artist.id).all()
  artists = []
  for artist in db_artists:
    artists.append({
      "id": artist[0],
      "name": artist[1],
      "num_upcoming_shows": artist[2],
    })
  # end for
  response={
    "count": len(db_artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  artist = Artist.query.get(artist_id)

  if artist is None : return

  db_past_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show).filter(Show.artist_id == artist_id, Show.start_time <= datetime.utcnow()).all()
  past_shows = []
  for venue_id, venue_name, venue_image_link, show_start_time in db_past_shows:
    past_shows.append({
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": show_start_time
    })
  db_upcoming_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(Show).filter(Show.artist_id == artist_id, Show.start_time > datetime.utcnow()).all()
  upcoming_shows = []
  for venue_id, venue_name, venue_image_link, show_start_time in db_upcoming_shows:
    upcoming_shows.append({
        "venue_id": venue_id,
        "venue_name": venue_name,
        "venue_image_link": venue_image_link,
        "start_time": show_start_time 
    })
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    # "seeking_talent": artist.is_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    # "seeking_talent": artist.is_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  if artist is not None:
      # Update the artist attributes based on the data in the request
      data = request.form
      artist.name = data.get('name', artist.name)
      artist.city = data.get('city', artist.city)
      artist.state = data.get('state', artist.state)
      artist.phone = data.get('phone', artist.phone)
      artist.image_link = data.get('image_link', artist.image_link)
      artist.facebook_link = data.get('facebook_link', artist.facebook_link)
      artist.genres = ','.join(data.get('genres', artist.genres.split(',')))
      artist.website_link = data.get('website_link', artist.website_link)
      artist.seeking_description = data.get('seeking_description', artist.seeking_description)
      artist.is_talent = data.get('seeking_talent', artist.is_talent)
      db.session.commit()
      return redirect(url_for('show_artist', artist_id=artist_id))
  else:
      # If the venue is not found, return a 404 error
      return jsonify({'message': 'Venue not found'}), 404


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)

  if venue is None : return
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.is_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
  }
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  if venue is not None:
      # Update the venue attributes based on the data in the request
      data = request.form
      venue.name = data.get('name', venue.name)
      venue.city = data.get('city', venue.city)
      venue.state = data.get('state', venue.state)
      venue.address = data.get('address', venue.address)
      venue.phone = data.get('phone', venue.phone)
      venue.image_link = data.get('image_link', venue.image_link)
      venue.facebook_link = data.get('facebook_link', venue.facebook_link)
      venue.genres = ','.join(data.get('genres', venue.genres.split(',')))  # Convert genres list to string
      venue.website_link = data.get('website_link', venue.website_link)
      venue.seeking_description = data.get('seeking_description', venue.seeking_description)
      venue.is_talent = data.get('seeking_talent', venue.is_talent)
      db.session.commit()
      return redirect(url_for('show_venue', venue_id=venue_id))
  else:
      # If the venue is not found, return a 404 error
      return jsonify({'message': 'Venue not found'}), 404

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  artist = Artist()

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.image_link = request.form['image_link']
  artist.facebook_link = request.form['facebook_link']
  artist.genres = request.form['genres']
  artist.website_link = request.form['website_link']
  artist.seeking_description = request.form['seeking_description']
  artist.is_talent = False if request.form.get('seeking_talent') is None else True

  regex = r"""\d{3}-\d{3}-\d{4}"""
  if not re.search(regex, artist.phone):
    flash('Phone invalid')
    return render_template('pages/home.html')
  
  try:
    db.session.add(artist)
    db.session.commit()
  except Exception as e:
    flash('An error occurred. Artist ' + artist.name + ' could not be listed. \n Error: ' + e)
  finally:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  venues_artists_shows = db.session.query(
        Venue.id,
        Venue.name,
        Artist.id,
        Artist.name,
        Artist.image_link,
        Show.start_time
    ).select_from(
        Venue
    ).join(
        Show, Venue.id == Show.venue_id
    ).join(
        Artist, Show.artist_id == Artist.id
    ).all()
  data = []
  for venue_id, venue_name, artist_id, artist_name, artist_image_link, show_start_time in venues_artists_shows:
      data.append({
          "venue_id": venue_id,
          "venue_name": venue_name,
          "artist_id": artist_id,
          "artist_name": artist_name,
          "artist_image_link": artist_image_link,
          "start_time": show_start_time
      })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  start_time = request.form.get('start_time')
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')

  if venue_id is None and venue_id == '':
    flash('Venue ID invalid')
    return render_template('pages/home.html')
  
  if artist_id is None and artist_id == '':
    flash('Artist ID invalid')
    return render_template('pages/home.html')
  
  if start_time is None and start_time == '':
    flash('Start time invalid')
    return render_template('pages/home.html')

  show = Show()
  show.start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
  show.venue_id = try_parse_int(venue_id)
  show.artist_id = try_parse_int(artist_id)
  
  try:
    db.session.add(show)
    db.session.commit()
  except Exception as e:
    raise e
  finally:
    flash('Show was successfully listed!')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
