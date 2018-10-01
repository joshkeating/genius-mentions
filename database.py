# code to process data for the database

import sqlite3
from sqlite3 import Error
import csv


# creates SQLite db in the /db dir, creates songs and artists tables
# throws error if connection is not established
def createDB(db):
    try:
        # establish db connection
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
 

def loadfromCSV(sourceFile):
    
    conn = sqlite3.connect("./db/geniusSQLite.db")
    c = conn.cursor()

    csvfile =  open(sourceFile, newline='')

    # this double pass over the file probaby isnt necessary
    songReader = csv.DictReader(csvfile, delimiter=';', quotechar='|')
    artistReader = csv.DictReader(csvfile, delimiter=';', quotechar='|')

    # create list of tuples using DictReader
    songData = [(row['song_id'], row['title'], row['title_with_featured'],
        row['url'], row['album'], row['full_date'], row['date_month'],
        row['date_year'], row['lyrics'], row['primary_artist_id']) for row in songReader]
    
    artistData = [(row['primary_artist_id'], row['primary_artist_name']) for row in artistReader]

    c.executemany("INSERT OR IGNORE INTO artists VALUES (?,?);", artistData)
    c.executemany("INSERT OR IGNORE INTO songs VALUES (?,?,?,?,?,?,?,?,?,?);", songData)

    conn.commit()
    csvfile.close()
    
    return



def fullUpdate():
    return

def updateArtist(artistName):
    return



# createDB("./db/geniusSQLite.db")

loadfromCSV("./data/output/full-ao1.csv")