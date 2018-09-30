# code to process data for the database

import sqlite3
from sqlite3 import Error

def createDB(db):
    try:
        conn = sqlite3.connect(db)
        print("SQLite database version: " + sqlite3.version + " created.")

        c = conn.cursor()
        # Create tables

        c.execute('''CREATE TABLE artists (
                        artist_id INTEGER PRIMARY KEY,
                        artist_name TEXT NOT NULL
                     )''')
        print("Artists table created.")

        c.execute('''CREATE TABLE songs (
                        id INTEGER PRIMARY KEY,
                        title TEXT NOT NULL, 
                        title_with_featured TEXT NOT NULL,
                        url TEXT NOT NULL,
                        album TEXT NOT NULL,
                        full_date TEXT,
                        date_month TEXT,
                        date_year TEXT,
                        lyrics TEXT,
                        primary_artist_id INTEGER NOT NULL,
                                FOREIGN KEY (primary_artist_id) REFERENCES artists(artist_id)
                     )''')
        print("Songs table created.")

    except Error as e:
        print(e)
    finally:
        conn.close()
    return
 
def fullUpdate():
    return

def updateArtist(artistName):
    return



createDB("./db/geniusSQLite.db")