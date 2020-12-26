#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import datetime
# here I tried to import the model classes from models.py (ike: from models import Show), but it will cause a circle importing error, so I imported the whole file instead
import models
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config.DatabaseURI')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  -------------------------------------------------------- --------

@app.route('/venues')
def venues():

  locals = []
  venues = models.Venue.query.all()
  for place in models.Venue.query.distinct(models.Venue.city, models.Venue.state).all():
      locals.append({
          'city': place.city,
          'state': place.state,
          'venues': [{
              'id': venue.id,
              'name': venue.name,
          } for venue in venues if
              venue.city == place.city and venue.state == place.state]
      })

  areas = []
  return render_template('pages/venues.html', areas=locals);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  
  search =request.form.get('search_term', '')
  venues = models.Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()
  # source for how to deal with ilike: https://docs.sqlalchemy.org/en/14/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike

  response = {}
  dataDict = {}
  response['count'] = len(venues)
  response['data'] = []

  for venue in venues:
    dataDict['id'] = venue.id 
    dataDict['name'] = venue.name
    response['data'].append(dataDict.copy())

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  now = datetime.datetime.now()
  nextShowinArray = {} 
  upcoming_shows = []
  past_shows = []

  venue = models.Venue.query.filter_by(id=venue_id).first()

  # retrive the upcomming shows using join with Show model and Venue model
  upcoming_shows_qurey = db.session.query(models.Show).join(models.Venue, models.Show.venue_id== venue_id).filter(models.Show.created_at> now)
  # insert each show in a seperated dict and append each dict to a list
  for show in upcoming_shows_qurey:
    nextShowinArray['artist_id'] = show.artist_id
    nextShowinArray['artist_name'] = show.artist.name
    nextShowinArray['artist_image_link'] = show.artist.image_link
    nextShowinArray['start_time'] = str(show.created_at)
    upcoming_shows.append(nextShowinArray.copy())

  # retrive the upcomming shows using join with Show model and Venue model
  past_shows_qurey = db.session.query(models.Show).join(models.Venue, models.Show.venue_id== venue_id).filter(models.Show.created_at < now)
  # insert each show in a seperated dict and append each dict to a list
  for show in past_shows_qurey:
    nextShowinArray['artist_id'] = show.artist_id
    nextShowinArray['artist_name'] = show.artist.name
    nextShowinArray['artist_image_link'] = show.artist.image_link
    nextShowinArray['start_time'] = str(show.created_at)
    past_shows.append(nextShowinArray.copy())

  data ={
    "id": venue_id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
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
  # get values from the form
  form = VenueForm() 
  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.address.data
  phone = form.phone.data
  genres = form.genres.data
  facebook_link = form.facebook_link.data
  website = form.website.data
  seeking_talent = form.seeking_talent.data
  seeking_description = form.seeking_description.data
  image_link = form.image_link.data
   
  # sessions & try source: https://docs.sqlalchemy.org/en/13/orm/session_basics.html
  try:
    # insert to Venue
    insertedVenue = models.Venue(name = name, city = city, state = state, address = address, phone = phone, image_link = image_link,facebook_link = facebook_link ,website = website, seeking_talent = seeking_talent, genres = genres, seeking_description= seeking_description)
    db.session.add(insertedVenue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:
    flash('An error occurred. Venue ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close()
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE'])
def delete_venue(venue_id):

  venue = models.Venue.query.filter_by(id=venue_id).first()
  if venue:
    try:
      db.session.delete(venue)
      db.session.commit()
      flash('Venue ' + name + ' was successfully deleted!')
    except:
      flash('An error occurred. Venue ' + name + ' could not be deleted.')
      db.session.rollback()
    finally:
      db.session.close()
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  artists = models.Artist.query.all()
  artistsDict = {}
  for artist in artists:
    artistsDict['id'] = artist.id 
    artistsDict['name'] = artist.name
    data.append(artistsDict.copy())

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search =request.form.get('search_term', '')
  artists = models.Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()
  # source for how to deal with ilike: https://docs.sqlalchemy.org/en/14/orm/internals.html?highlight=ilike#sqlalchemy.orm.attributes.QueryableAttribute.ilike

  response = {}
  dataDict = {}
  response['count'] = len(artists)
  response['data'] = []

  for artist in artists:
    dataDict['id'] = artist.id 
    dataDict['name'] = artist.name
    response['data'].append(dataDict.copy())
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  now = datetime.datetime.now()
  nextShowinArray = {} 
  upcoming_shows = []
  past_shows = []
  artist = models.Artist.query.filter_by(id=artist_id).first()
  
  # retrive the upcomming shows using join with Show model and Artist model
  upcoming_shows_qurey = db.session.query(models.Show).join(models.Artist, models.Show.artist_id == artist_id).filter(models.Show.created_at > now)
  # insert each show in a seperated dict and append each dict to a list
  for show in upcoming_shows_qurey:
    nextShowinArray['venue_id'] = show.venue_id
    nextShowinArray['venue_name'] = show.venue.name
    nextShowinArray['venue_image_link'] = show.venue.image_link
    nextShowinArray['start_time'] = str(show.created_at)
    upcoming_shows.append(nextShowinArray.copy())

  # retrive the upcomming shows using join with Show model and Artist model
  past_shows_qurey = db.session.query(models.Show).join(models.Artist, models.Show.artist_id == artist_id).filter(models.Show.created_at < now)
  # insert each show in a seperated dict and append each dict to a list
  for show in past_shows_qurey:
    nextShowinArray['venue_id'] = show.venue_id
    nextShowinArray['venue_name'] = show.venue.name
    nextShowinArray['venue_image_link'] = show.venue.image_link
    nextShowinArray['start_time'] = str(show.created_at)
    past_shows.append(nextShowinArray.copy())

  shows = models.Show.query.filter_by(artist=artist).all()

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
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
  artist = models.Artist.query.filter_by(id=artist_id).first()
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.website.data = artist.website
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # here I reimported it to avoid this error => Object '<>' is already attached to session '1' (this is '2'), avoid two sessions  
  from models import db
  form = ArtistForm()
  try:
    artist = models.Artist.query.filter_by(id=artist_id).first()
    if artist:
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = form.genres.data
      artist.facebook_link = form.facebook_link.data
      artist.website = form.website.data 
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data
      artist.image_link = form.image_link.data
      db.session.add(artist)
      db.session.commit()
  except:
    flash('An error occurred. Artist ' + form.name.data + ' could not be edited.')
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = models.Venue.query.filter_by(id=venue_id).first()
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.website.data = venue.website
  form.image_link.data = venue.image_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  from models import db
  form = VenueForm()
  try:
    venue = models.Venue.query.filter_by(id=venue_id).first()
    if venue:
      venue.name = form.name.data
      venue.city = form.city.data 
      venue.state = form.state.data 
      venue.address = form.address.data 
      venue.phone = form.phone.data 
      venue.genres = form.genres.data 
      venue.facebook_link = form.facebook_link.data 
      venue.website = form.website.data 
      venue.seeking_talent = form.seeking_talent.data 
      venue.seeking_description = form.seeking_description.data 
      venue.image_link = form.image_link.data 
      db.session.add(venue)
      db.session.commit()
  except:
    flash('An error occurred. Venue ' + form.name.data + ' could not be edited.')
    db.session.rollback()
  finally:
    db.session.close()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  name = form.name.data
  city =  form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  facebook_link = form.facebook_link.data
  website = form.website.data
  seeking_venue = form.seeking_venue.data
  seeking_description = form.seeking_description.data
  image_link = form.image_link.data

  try:
    insertedArtist = models.Artist(name = name, city = city, state = state, phone = phone, image_link = image_link,facebook_link = facebook_link ,website = website, seeking_venue = seeking_venue, genres = genres, seeking_description= seeking_description)
    db.session.add(insertedArtist)
    db.session.commit()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + name + ' could not be listed.')
    db.session.rollback()
  finally:
    db.session.close() 
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  AllShows = models.Show.query.all()
  showsDict = {}

  for show in AllShows:
    showsDict['venue_id'] = show.venue_id
    showsDict['artist_id'] = show.artist_id
    showsDict['venue_name'] = show.venue.name
    showsDict['artist_name'] = show.artist.name
    showsDict['artist_image_link'] = show.artist.image_link
    showsDict['start_time'] = str(show.created_at)
    data.append(showsDict.copy())

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  form = ShowForm()
  artist_id = form.artist_id.data
  artist = models.Artist.query.filter_by(id=artist_id).first()

  venue_id = form.venue_id.data
  venue = models.Venue.query.filter_by(id=venue_id).first()

  start_time = form.start_time.data

  if artist and venue:
    from models import db
    try:
      new_show = models.Show(artist = artist,venue= venue, created_at = start_time)
      db.session.add(new_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except:
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
    finally:
      db.session.close()
    return render_template('pages/home.html')

  flash('An error occurred. Show could not be listed.')
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
