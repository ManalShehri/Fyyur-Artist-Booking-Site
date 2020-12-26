import os

class DatabaseURI:
    SECRET_KEY = os.urandom(32)

    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Enable debug mode.
    DEBUG = True

    # declear the DB URI parts
    DATABASE_NAME = "fyyur"
    username = 'manal'
    password = '123456m'
    url = 'localhost:5432'

    # Connect to the database
    SQLALCHEMY_DATABASE_URI = "postgres://{}:{}@{}/{}".format(username, password, url, DATABASE_NAME)