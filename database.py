# code to process data for the database

import sqlite3
from sqlite3 import Error
import csv
import requests
import json
import urllib.request
from bs4 import BeautifulSoup as bs
import re


def createDB(db):
    """ 
    creates SQLite db in the /db dir, creates songs and artists tables
    throws error if connection is not established
    """

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
    """ Adds contents of provided csv file to the database """

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
    """ Truncates all tables in the database"""

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
    """ docstring TODO:"""
    return


def updateArtist(artistName):
    """ Add a docstring here """

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
        conn.commit()

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

                if c.fetchone() == (0,):

                    title = song.get("title")
                    titleWithFeat = song.get("title_with_featured")
                    url = song.get("url")
                    primaryArtistId = song.get("primary_artist").get("id")
                    
                    # get additional metadata from bs scrape
                    try:
                        # define the regex to replace metadata we dont care about
                        pattern = r"\[.*\]|\(x[0-9]\)|\n"
                        targetPage = requests.get(url)
                        html = bs(targetPage.text, "html.parser")
                        dateMonth = "NA"
                        dateYear = "NA"
                        # get raw text from a couple of elements on the page
                        lyricsStandard = checkElementExistence(html.find("div", class_="lyrics"))
                        fullDate = checkElementExistence(html.find("span", class_="metadata_unit-info metadata_unit-info--text_only")) 
                        album = checkElementExistence(html.find("a", class_="song_album-info-title")).strip()

                        # process metadata
                        if fullDate != "NA":
                            splitDate = fullDate.split()
                            dateMonth = splitDate[0]
                            dateYear = splitDate[2]
                            
                        # remove annotations and extra spaces
                        lyricsTemp = re.sub(pattern, " ", lyricsStandard)
                        lyrics = re.sub(' +',' ',lyricsTemp)

                        # insert new record into database
                        newTuple = (int(songId), str(title), str(titleWithFeat), str(url), str(album),
                            str(fullDate), str(dateMonth), str(dateYear), str(lyrics), int(primaryArtistId))

                        c.execute("INSERT OR IGNORE INTO songs VALUES (?,?,?,?,?,?,?,?,?,?);", newTuple)
                        conn.commit()
                        recordsProcessed += 1
                    
                    except IndexError:
                        print("Malformed html data")
                    except Error as e:
                        print(e)

            print("Batch processed...", recordsProcessed, "new records found", sep=" ")

            if response["response"]["next_page"] == None:
                print("End of pages reached, Exiting")
                pageStatus = False
            
            currentPage += 1

        except Error as e:
            print(e)
    
    conn.close()

    print()
    print(recordsProcessed, "new records inserted into the songs table!", sep=" ")

    return


def getArtistId(artistName):
    """ Takes in an artist name and returns the Genius ID for that artist """

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
    

def getToken():
    """ Opens the file that stores the api keys, returns the Genius APi access token """

    with open('./secrets.json') as secrets:
        return json.load(secrets).get("access_token")


def checkElementExistence(input):
    """ Takes in a html object and checks to see that it is valid """

    if input is None:
        return "NA"
    else:
        return input.get_text()


# run functions

# updateArtist("Young Thug")

# createDB("./db/geniusSQLite.db")

# clearDatabase()

# loadfromCSV("./data/output/all.csv")
