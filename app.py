#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://nisp78@localhost:5432/fyyur'
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'Show'

    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return 'Show(%s, %s)' % (self.venue_id, self.artist_id)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_description = db.Column(db.String(300), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=True)
    past_shows = db.Column(db.String(500))
    upcoming_shows = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show', backref='venue', lazy=True)


    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean, nullable=False, default=True)
    seeking_description = db.Column(db.String(300), nullable=False)
    past_shows = db.Column(db.String(500))
    upcoming_shows = db.Column(db.String(500))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

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
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # implement search on artists with partial string search.
    venue_query = Venue.query.filter(Venue.name.ilike('%' + request.form['search_term'] + '%'))
    venue_list = list(map(Venue.short, venue_query))
    response = {
      "count": len(venue_list),
      "data": venue_list
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get('search_term', '')
    )

@app.route('/venues')
def venues():
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
  venue_state_and_city = ''
  data = []

  # by a loop it will be possible to check for upcoming shows, city, states and venues
  for venue in venues:
    #The filter is applied by establishing that the show start time is greater than the current time
    print(venue)
    upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()
    if venue_state_and_city == venue.city + venue.state:
      data[len(data) - 1]["venues"].append({
        "id": venue.id,
        "name":venue.name,
        "num_upcoming_shows": len(upcoming_shows) # counts the number of shows
      })
    else:
      venue_state_and_city == venue.city + venue.state
      data.append({
        "city":venue.city,
        "state":venue.state,
        "venues": [{
          "id": venue.id,
          "name":venue.name,
          "num_upcoming_shows": len(upcoming_shows)
        }]
      })
      return render_template('pages/venues.html', areas=data)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # here we get all venues
    venue = Venue.query.filter_by(id=venue_id).first()

    # here we get all shows for each venue
    shows = Show.query.filter_by(venue_id=venue_id).all()

    # function that returns upcoming shows
def upcoming_shows():
    upcoming = []
    for show in shows:
        if show.start_time > datetime.now():
            upcoming.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
            })
        return upcoming
 # function that returns past shows
def past_shows():
    past = []
    for show in shows:
        if show.start_time < datetime.now():
            past.append({
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data concerning each venue
    data = {
        "id": venue.id,
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
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
    }

    # return template with venue data
    return render_template('pages/show_venue.html', venue=data)



#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    data = request.form
    vname = data['name']
    vcity = data['city']
    vstate = data['state']
    vaddress = data['address']
    vphone = data['phone']
    vgenres = data['genres']
    vfb_link = data['facebook_link']
    vimage_link = data['image_link']
    try:
        db.session.add(Venue(
            city=vcity,
            state=vstate,
            name=vname,
            address=vaddress,
            phone=vphone,
            facebook_link=vfb_link,
            genres=vgenres,
            seeking_talent=False,
            website="",
            image_link=vimage_link
        ))
    except expression:
        error = true
    finally:
        if not error:
            db.session.commit()
            flash('Venue ' + request.form['name'] +
                  ' was successfully listed!')
        else:
            flash('An error occurred. Venue ' +
                  vname + ' could not be listed.')
            db.session.rollback()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('The Venue has been successfully deleted!')
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        flash('Delete was unsuccessful. Try again!')
    finally:
        db.session.close()
    return None

#  Artists
#  ----------------------------------------------------------------

# Here the controller manages the overview page
@app.route('/artists')
def artists():
    data = []
    artists = Artist.query.all()
    for artist in artists:
        data.append({
        "id": artist.id,
        "name": artist.name
        })
    return render_template('pages/artists.html', artists=data)

# here the controller manages the search function of the app
@app.route('/artists/search', methods=['POST'])
def search_artists():
    # search term is obtained from user input
    search_term = request.form.get('search_term', '')

    # Here artists matching the search term are found
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(artists),
        "data": []
    }

    # for all matching artists, the num of upcoming shows is obtained
    # and data is added to the reponse
    for artist in artists:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(artist_id=artist.id).all()

        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows,
        })

    # return reponse with matching search results
    return render_template('pages/search_artists.html', results=response,
    search_term=request.form.get('search_term', ''))

# Here the controller handles individual artist page
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
     # this finds artist by id
    data = Artist.query.filter_by(id=artist_id).first()
    # this matches shows with artist id
    shows = Show.query.filter_by(artist_id=artist_id).all()
    # returns upcoming shows
def upcoming_shows():
    upcoming = []
    # if the show is upcoming, add to upcoming
    for show in shows:
        if show.start_time > datetime.now():
            upcoming.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
            })
        return upcoming

# Here past shows are returned
def past_shows():
    past = []
    for show in shows:
        if show.start_time < datetime.now():
            past.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
                })
        return past

# data for given artist
        data = {
        "id": artist.id,
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
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows()),
        }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
# here the controller manages the edit artist form
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist_query = Artist.query.get(artist_id)
    if artist_query:
        artist_details = Artist.details(artist_query)
        form.name.data = artist_details["name"]
        form.genres.data = artist_details["genres"]
        form.city.data = artist_details["city"]
        form.state.data = artist_details["state"]
        form.phone.data = artist_details["phone"]
        form.website.data = artist_details["website"]
        form.facebook_link.data = artist_details["facebook_link"]
        form.seeking_venue.data = artist_details["seeking_venue"]
        form.seeking_description.data = artist_details["seeking_description"]
        form.image_link.data = artist_details["image_link"]
        return render_template('forms/edit_artist.html', form=form, artist=artist_details)
    return render_template('errors/404.html')

# here the controller manages the edit artist submission form
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    try:
        form = ArtistForm()
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        # here the phone number is validated
        phone_validator(artist.phone)
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website.data
        artist.seeking_venue = True if form.seeking_venue.data == 'Yes' else False
        artist.seeking_description = form.seeking_description.data

        # here changes are committed
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except ValidationError as e:
        # in case of validation errors session is rolledback
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed. ' + str(e))
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    # return redirect to artist page
    return redirect(url_for('show_artist', artist_id=artist_id))

# here the controller manages the edit venue section of the app
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue_query = Venue.query.get(venue_id)
    if venue_query:
        venue_details = Venue.details(venue_query)
        form.name.data = venue_details["name"]
        form.genres.data = venue_details["genres"]
        form.address.data = venue_details["address"]
        form.city.data = venue_details["city"]
        form.state.data = venue_details["state"]
        form.phone.data = venue_details["phone"]
        form.website.data = venue_details["website"]
        form.facebook_link.data = venue_details["facebook_link"]
        form.seeking_talent.data = venue_details["seeking_talent"]
        form.seeking_description.data = venue_details["seeking_description"]
        form.image_link.data = venue_details["image_link"]
        return render_template('forms/edit_venue.html', form=form, venue=venue_details)
    return render_template('errors/404.html')

# here the controller manages the edit venue submission form
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    try:
        form = VenueForm()
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.address = form.address.data
        venue.phone = form.phone.data
        # here the phone number is validated
        phone_validator(venue.phone)
        venue.facebook_link = form.facebook_link.data
        venue.website = form.website.data
        venue.image_link = form.image_link.data
        venue.seeking_talent = True if form.seeking_talent.data == 'Yes' else False
        venue.seeking_description = form.seeking_description.data

        # here changes are committed
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except ValidationError as e:
        # in case of validation errors session is rolledback
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed. ' + str(e))
    except:
        # in case of other errors session is rolledback
        db.session.rollback()
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------
# Here new artist is created
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    new_artist = Artist()
    new_artist.__dict__.update(request.form)
    genres = ', '.join(request.form.getlist('genres'))
    new_artist.genres = genres
    if 'seeking_venue' in request.form:
        new_artist.seeking_venue = True
    else:
        new_artist.seeking_venue = False
    try:
        db.session.add(new_artist)
        db.session.commit()
        flash(f'{new_artist.name} is now listed!')
    except:
        flash(f'An error occurred. {new_artist.name} could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')
# Here new artist is deleted
@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):

    # catch exceptions with try-except block
    try:
        # get artist by id
        artist = Artist.query.filter_by(id=artist_id).first()
        name = artist.name

        # delete artist and commit changes
        db.session.delete(artist)
        db.session.commit()

        flash('Artist ' + name + ' was successfully deleted.')
    except:
        # rollback if exception
        db.session.rollback()

        flash('An error occurred. Artist ' + name + ' could not be deleted.')
    finally:
        # always close the session
        db.session.close()

    return jsonify({'success': True})

#  Shows
#  ----------------------------------------------------------------
# Here the controller displays the show page
@app.route('/shows')
def shows():
    shows = Show.query.all()
    data = []
    for show in shows:
        data.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
        })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
  # renders form. do not touch.
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # Here new shows are created in the database
  try:
    new_show = Show(
      venue_id=request.form['venue_id'],
      artist_id=request.form['artist_id'],
      start_time=request.form['start_time'],
    )
    Show.insert(new_show)

    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except SQLAlchemyError as e:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    flash('An error occured. Show could not be listed.')
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
