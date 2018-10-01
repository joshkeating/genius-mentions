# code to process data for the database

import sqlite3
from sqlite3 import Error
import csv

import requests
import json
import urllib.request

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
 

# adds contents of provided csv file to the database
def loadfromCSV(sourceFile):
    try:
        conn = sqlite3.connect("./db/geniusSQLite.db")
        c = conn.cursor()

        csvfile =  open(sourceFile, newline='')
        reader = csv.DictReader(csvfile, delimiter=';', quotechar='|')

        songData = []
        artistData = []

        for row in reader:
            songData.append((row['song_id'], row['title'], row['title_with_featured'],
            row['url'], row['album'], row['full_date'], row['date_month'],
            row['date_year'], row['lyrics'], row['primary_artist_id']))
            artistData.append((row['primary_artist_id'], row['primary_artist_name']))

        csvfile.close()

        c.executemany("INSERT OR IGNORE INTO artists VALUES (?,?);", artistData)
        c.executemany("INSERT OR IGNORE INTO songs VALUES (?,?,?,?,?,?,?,?,?,?);", songData)

    except Error as e:
        print(e)
    finally:
        conn.commit()
        conn.close()
    return


def clearDatabase():
    try:
        # establish db connection
        conn = sqlite3.connect('./db/geniusSQLite.db')
        c = conn.cursor()
        c.execute('DELETE FROM artists')
        c.execute('DELETE FROM songs')
        conn.commit()
        c.execute('VACUUM')
        print("All tables truncated.")
    except Error as e:
        print(e)
    finally:
        conn.close()
    return



def fullUpdate():
    return

def updateArtist(artistName):

    # check if artist exists in db
    artistId = getArtistId(artistName)

    if artistId == -1:
        print("Specified artist does not exist!")
        return

    # establish connection with database
    conn = sqlite3.connect('./db/geniusSQLite.db')
    c = conn.cursor()

    aid = (artistId,)
    c.execute('SELECT COUNT(*) FROM artists WHERE artist_id=?', aid)

    if c.fetchone() == (0,):

        print("Adding " + artistName + " to database")
        c.execute("INSERT INTO artists VALUES (?,?);", (artistId, artistName))
        conn.commit()
    else:
        print(artistName + " currently exists in the database")


    # songId, title, titleWithFeat, url, primaryArtistId
    tempDict = []

    currentPage = 1
    pageStatus = True
    recordsProcessed = 0

    while pageStatus == True:

        try:
            query = "https://api.genius.com/artists/" + str(artistId) + "/songs?per_page=50&page=" + str(currentPage)
            request = urllib.request.Request(query)
            # add authentication headers
            request.add_header("Authorization", "Bearer " + getToken())
            request.add_header("User-Agent", "")
            # deserialize to python dict
            response = json.load(urllib.request.urlopen(request))
            songList = response.get("response").get("songs")

            for song in songList:

                songId = song.get("id")

                sid = (songId,)
                c.execute('SELECT COUNT(*) FROM songs WHERE id=?', sid)

                if c.fetchone() != (0,):

                    title = song.get("title")
                    titleWithFeat = song.get("title_with_featured")
                    url = song.get("url")
                    primaryArtistId = song.get("primary_artist").get("id")

                    tempDict.append((songId, title, titleWithFeat, url, primaryArtistId))

                    recordsProcessed += 1
                

            print("Batch processed...", recordsProcessed, "new records proccesed", sep=" ")

            
            if response["response"]["next_page"] == None:
                print("End of pages reached, Exiting")
                pageStatus = False
            
            currentPage += 1

        except:
            print("Something broke!")
    
    print(tempDict)

    # get additional metadata from bs scrape

    # add songs that do not exist

    conn.close()

    return


def getArtistId(artistName):

    # form query
    query = "https://api.genius.com/search?q=" + urllib.request.quote(artistName)
    request = urllib.request.Request(query)

    # add authentication headers
    request.add_header("Authorization", "Bearer " + getToken())
    request.add_header("User-Agent", "")

    # deserialize to python dict
    response = json.load(urllib.request.urlopen(request))

    # if artist does not exist
    if len(response["response"]["hits"]) == 0:
        return -1

    # grab id from dict
    return response["response"]["hits"][0]["result"]["primary_artist"]["id"]
    
        



# get access tokens from file
def getToken():
    with open('./secrets.json') as secrets:
        return json.load(secrets).get("access_token")




updateArtist("Young Thug")

# createDB("./db/geniusSQLite.db")

# clearDatabase()

# loadfromCSV("./data/output/full-ao1.csv")
