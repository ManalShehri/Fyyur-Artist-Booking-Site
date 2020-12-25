import json
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
import datetime
from app import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column('venue_id',db.Integer, db.ForeignKey('Venue.id'))
    artist_id = db.Column('artist_id',db.Integer, db.ForeignKey('Artist.id'))
    created_at = db.Column(db.DateTime, default = datetime.datetime.now)
    venue = db.relationship("Venue", back_populates="artist")
    artist = db.relationship("Artist", back_populates="venue")  
    
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
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))

    artist = db.relationship("Show", back_populates="venue", cascade="all, delete-orphan")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Done)

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500))
  
    venue = db.relationship("Show", back_populates="artist", cascade="all, delete-orphan")




