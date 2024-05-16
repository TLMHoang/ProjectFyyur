from datetime import datetime
import os
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from flask_moment import Moment


db = SQLAlchemy()

def setup_db(app):
    with app.app_context():
        # app.config["SQLALCHEMY_DATABASE_URI"] = database_path
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        db.app = app
        db.init_app(app)
        db.create_all()
    # db = SQLAlchemy(app)
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


# def seed_data():
#     # Create venues
#     venue1 = Venue(name='Quan 1', city='Ho Chi Minh', state='AL', address='Quan 1 - Ho Chi Minh', phone='000-000-0000')
#     venue2 = Venue(name='Quan 2', city='Ho Chi Minh', state='AL', address='Quan 2 - Ho Chi Minh', phone='000-000-0000')
#     venue3 = Venue(name='Quan 3', city='Ho Chi Minh', state='AL', address='Quan 3 - Ho Chi Minh', phone='000-000-0000')
#     venue4 = Venue(name='Cau Giay', city='Ha Noi', state='AZ', address='Cau Giay - Ha Noi', phone='000-000-0000')
#     venue5 = Venue(name='Long Bien', city='Ha Noi', state='AZ', address='Long Bien - Ha Noi', phone='000-000-0000')
#     venue6 = Venue(name='Cau Rong', city='Da Nang', state='AK', address='Cau Rong - Da Nang', phone='000-000-0000')

#     # Create artists
#     artist1 = Artist(name='Ca si A', city='Ho Chi Minh', state='AL', phone='000-000-0000')
#     artist2 = Artist(name='Ca si B', city='Ha Noi', state='AZ', phone='000-000-0000')
#     artist3 = Artist(name='Ca si C', city='Da Nang', state='AK', phone='000-000-0000')
#     artist4 = Artist(name='Ca si D', city='Ho Chi Minh', state='AL', phone='000-000-0000')
#     artist5 = Artist(name='Ca si E', city='Da Nang', state='AK', phone='000-000-0000')
#     artist6 = Artist(name='Ca si F', city='Ha Noi', state='AZ', phone='000-000-0000')

#     # Add venues and artists to session
#     db.session.add_all([venue1, venue2, venue3, venue4, venue5, venue6, artist1, artist2, artist3, artist4, artist5, artist6])
#     db.session.commit()

#     # Generate shows for each artist
#     artists = [artist1, artist2, artist3, artist4, artist5, artist6]
#     venues = [venue1, venue2, venue3, venue4, venue5, venue6]

#     for artist in artists:
#         # Select random venues for the artist's shows
#         artist_venues = random.sample(venues, 4)
        
#         for venue in artist_venues:
#             # Generate show times
#             start_time = datetime.utcnow() + timedelta(days=random.randint(1, 30), hours=random.randint(1, 23), minutes=random.randint(0, 59))
            
#             # Create show
#             show = Show(start_time=start_time, venue=venue, artist=artist)
#             db.session.add(show)

#     # Commit all changes
#     db.session.commit()