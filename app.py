# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

from datetime import timedelta
import json
import random
import dateutil.parser
import babel
import re
from flask import Flask, abort, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import and_, func
from forms import *
from flask_migrate import Migrate

from model import Artist, Show, Venue, setup_db, db
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')


setup_db(app)
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# function helper
# ----------------------------------------------------------------------------#
def try_parse_int(value):
    try:
        return int(value)
    except ValueError:
        return None

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    try:
        group_venues = db.session.query(Venue.state, Venue.city).group_by(
            Venue.state, Venue.city).all()

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
    except:
        return render_template('errors/500.html')
        


@app.route('/venues/search', methods=['POST'])
def search_venues():
    try:
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
        response = {
            "count": len(venues),
            "data": venues
        }
        return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        return render_template('errors/500.html')
    


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)

        past_shows = Show.query.filter(
            Show.venue_id == venue_id, Show.start_time <= datetime.utcnow()).all()
        upcoming_shows = Show.query.filter(
            Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).all()

        data = {
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
    except:
        return render_template('errors/500.html')

    

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        venue_form = VenueForm(request.form)
        if request.method == 'POST' and not venue_form.validate_on_submit():
            flash('Data invalid')
            return render_template('pages/home.html')

        venue = Venue()
        venue.name = venue_form.name.data,
        venue.city = venue_form.city.data,
        venue.state = venue_form.state.data,
        venue.address = venue_form. address.data,
        venue.phone = venue_form.phone.data,
        venue.genres = venue_form.genres.data,
        venue.facebook_link = venue_form.facebook_link.data,
        venue.image_link = venue_form.image_link.data
        venue.website_link = venue_form.website_link.data
        venue.seeking_description = venue_form.seeking_description.data
        venue.is_talent = False if request.form.get(
            'seeking_talent') is None else True

        db.session.add(venue)
        db.session.commit()
        flash('Create {} success', venue.name)
        return render_template('pages/home.html')
    except Exception as e:
        flash('An error occurred. Venue ' + venue.name +
              ' could not be listed. \n Error: ' + e)
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)

        db.session.delete(venue)
        db.session.commit()
        flash('Delete {} success', venue.name)
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        return render_template('errors/500.html')
   
    

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    try:
        artists = db.session.query(Artist.id, Artist.name).all()
        data = []
        for artist in artists:
            data.append({
                "id": artist[0],
                "name": artist[1],
            })
        return render_template('pages/artists.html', artists=data)
    except:
        return render_template('errors/500.html')
    


@app.route('/artists/search', methods=['POST'])
def search_artists():
    try:
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
        response = {
            "count": len(db_artists),
            "data": artists
        }
        return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
    except:
        return render_template('errors/500.html')
    


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    try:
        artist = Artist.query.get_or_404(artist_id)

        db_past_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(
            Show).filter(Show.artist_id == artist_id, Show.start_time <= datetime.utcnow()).all()
        past_shows = []
        for venue_id, venue_name, venue_image_link, show_start_time in db_past_shows:
            past_shows.append({
                "venue_id": venue_id,
                "venue_name": venue_name,
                "venue_image_link": venue_image_link,
                "start_time": show_start_time
            })
        db_upcoming_shows = db.session.query(Venue.id, Venue.name, Venue.image_link, Show.start_time).join(
            Show).filter(Show.artist_id == artist_id, Show.start_time > datetime.utcnow()).all()
        upcoming_shows = []
        for venue_id, venue_name, venue_image_link, show_start_time in db_upcoming_shows:
            upcoming_shows.append({
                "venue_id": venue_id,
                "venue_name": venue_name,
                "venue_image_link": venue_image_link,
                "start_time": show_start_time
            })
        data = {
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
    except:
        return render_template('errors/500.html')

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    try:
        form = ArtistForm()
        artist = Artist.query.get_or_404(artist_id)
        artist = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres.split(','),
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website_link,
            "facebook_link": artist.facebook_link,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
        }
        # TODO: populate form with fields from artist with ID <artist_id>
        return render_template('forms/edit_artist.html', form=form, artist=artist)
    except:
        return render_template('errors/500.html')
    


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        artist = Artist.query.get_or_404(artist_id)

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
        artist.seeking_description = data.get(
            'seeking_description', artist.seeking_description)
        artist.is_talent = data.get('seeking_talent', artist.is_talent)
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        return render_template('errors/500.html')


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.get_or_404(venue_id)

        data = {
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
    except:
        return render_template('errors/500.html')
    


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        venue = Venue.query.get_or_404(venue_id)

        # Update the venue attributes based on the data in the request
        data = request.form
        venue.name = data.get('name', venue.name)
        venue.city = data.get('city', venue.city)
        venue.state = data.get('state', venue.state)
        venue.address = data.get('address', venue.address)
        venue.phone = data.get('phone', venue.phone)
        venue.image_link = data.get('image_link', venue.image_link)
        venue.facebook_link = data.get('facebook_link', venue.facebook_link)
        # Convert genres list to string
        venue.genres = ','.join(data.get('genres', venue.genres.split(',')))
        venue.website_link = data.get('website_link', venue.website_link)
        venue.seeking_description = data.get(
            'seeking_description', venue.seeking_description)
        venue.is_talent = data.get('seeking_talent', venue.is_talent)
        db.session.commit()
        return redirect(url_for('show_venue', venue_id=venue_id))
    except:
        return render_template('errors/500.html')

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        form = ArtistForm(request.form)
        if request.method == 'POST' and not form.validate_on_submit():
            flash('Data invalid')
            return render_template('errors/500.html')
        artist = Artist()

        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.genres = form.genres.data
        artist.website_link = form.website_link.data
        artist.seeking_description = form.seeking_description.data
        artist.is_talent = False if request.form.get(
            'seeking_talent') is None else True

        db.session.add(artist)
        db.session.commit()
        flash('Create {} success', artist.name)
        return render_template('pages/home.html')
    except Exception as e:
        flash('An error occurred. Artist ' + artist.name +
              ' could not be listed. \n Error: ' + e)
        db.session.rollback()
        return render_template('errors/500.html')
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
    try:
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
    except:
        return render_template('errors/500.html')
        
    


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():

    # if venue_id is None and venue_id == '':
    #     flash('Venue ID invalid')
    #     return render_template('pages/home.html')

    # if artist_id is None and artist_id == '':
    #     flash('Artist ID invalid')
    #     return render_template('pages/home.html')

    # if start_time is None and start_time == '':
    # flash('Start time invalid')
    # return render_template('pages/home.html')

    try:
        form = ShowForm()
        artist_id = form.artist_id.data
        venue_id = form.venue_id.data
        show = Show()
        show.start_time = form.start_time.data
        show.venue_id = try_parse_int(venue_id)
        show.artist_id = try_parse_int(artist_id)

        venue = Venue.query.get_or_404(show.venue_id)
        artist = Artist.query.get_or_404(show.artist_id)

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
        return render_template('pages/home.html')
    except Exception as e:
        db.session.rollback()
        return render_template('errors/500.html')

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
