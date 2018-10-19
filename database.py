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
 

def load_from_csv(source_file):
    """ Adds contents of provided csv file to the database """

    try:
        conn = sqlite3.connect("./db/geniusSQLite.db")
        c = conn.cursor()

        csvfile =  open(source_file, newline='')
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


def clear_database():
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


def update_artists_from_file(artist_file):
    """
    Takes in a text file with different artists seperated by newlines, adds each to the database. 
    CAUTION: this should not be run with too many artists per file otherwise the web scraping might be 
    interrupted or rate limited. Looks for files in the `./data/input/` dir.
    """

    source_file_path = "./data/input/" + artist_file

    # get names from file
    file = open(source_file_path, "r")
    name_list = file.readlines()

    for name in name_list:
        print("---- Processing: " + name)
        update_artist(name)
    
    return


def update_artist(artist_name):
    """
    Takes in an artist name string, checks to see if that artist exists in the Genius API, checks to see if 
    that arist exists in the sqlite db and adds to it if they do not. Processes all records relating to 
    artist in the Genius API and adds them to the sqlite db if it does not contain them already. For each new
    record, scrapes the associated url on genius.com for additional metadata.
    """

    # check if artist exists in db
    artist_id = get_artist_id(artist_name)

    if artist_id == -1:
        print("Specified artist does not exist in the Genius API.")
        return

    # establish connection with the local database
    conn = sqlite3.connect('./db/geniusSQLite.db')
    c = conn.cursor()

    aid = (artist_id,)
    c.execute('SELECT COUNT(*) FROM artists WHERE artist_id=?', aid)

    # check to see if artist_name exists in the sqlite database
    if c.fetchone() == (0,):

        print("Adding \'" + artist_name + "\' to database")
        c.execute("INSERT INTO artists VALUES (?,?);", (artist_id, artist_name.strip(' \t\n\r')))
        conn.commit()
    else:
        print("\'" + artist_name + "\' currently exists in the database")
        conn.commit()

    current_page = 1
    page_status = True
    records_processed = 0

    while page_status == True:

        try:
            query = "https://api.genius.com/artists/" + str(artist_id) + "/songs?per_page=50&page=" + str(current_page)
            request = urllib.request.Request(query)
            # add authentication headers
            request.add_header("Authorization", "Bearer " + get_token())
            request.add_header("User-Agent", "")
            # deserialize to python dict
            response = json.load(urllib.request.urlopen(request))
            songList = response.get("response").get("songs")

            for song in songList:

                songId = song.get("id")

                sid = (songId,)
                c.execute('SELECT COUNT(*) FROM songs WHERE id=?', sid)

                # if current song already exists in the sqlite database
                if c.fetchone() == (0,):

                    # get metadata from Genius API
                    title = song.get("title")
                    title_with_feat = song.get("title_with_featured")
                    url = song.get("url")
                    primary_artist_id = song.get("primary_artist").get("id")
                    
                    # get additional metadata from bs scrape
                    try:
                        # define the regex to replace metadata we dont care about
                        pattern = r"\[.*\]|\(x[0-9]\)|\n"
                        target_page = requests.get(url)
                        html = bs(target_page.text, "html.parser")
                        date_month = "NA"
                        date_year = "NA"
                        # get raw text from a couple of elements on the page
                        lyrics_standard = check_elem_exist(html.find("div", class_="lyrics"))
                        full_date = check_elem_exist(html.find("span", class_="metadata_unit-info metadata_unit-info--text_only")) 
                        album = check_elem_exist(html.find("a", class_="song_album-info-title")).strip()

                        # process date metadata
                        if full_date != "NA":
                            split_date = full_date.split()
                            date_month = split_date[0]
                            date_year = split_date[2]
                            
                        # remove annotations and extra spaces
                        lyrics_temp = re.sub(pattern, " ", lyrics_standard)
                        lyrics = re.sub(' +',' ',lyrics_temp)

                        # insert new record into database
                        newTuple = (int(songId), str(title), str(title_with_feat), str(url), str(album),
                            str(full_date), str(date_month), str(date_year), str(lyrics), int(primary_artist_id))

                        c.execute("INSERT OR IGNORE INTO songs VALUES (?,?,?,?,?,?,?,?,?,?);", newTuple)
                        conn.commit()
                        records_processed += 1
                    
                    except IndexError:
                        print("Missing or malformed html data")
                    except Error as e:
                        print(e)

            print("Batch processed...", records_processed, "total new records found.", sep=" ")

            if response["response"]["next_page"] == None:
                print("End of pages reached, Exiting")
                page_status = False
            
            current_page += 1

        except Error as e:
            print(e)
    
    conn.close()

    print()
    print(records_processed, "new records inserted into the songs table!", sep=" ")

    return


def get_artist_id(artist_name):
    """ Takes in an artist name and returns the Genius ID for that artist """

    # form query
    query = "https://api.genius.com/search?q=" + urllib.request.quote(artist_name)
    request = urllib.request.Request(query)

    # add authentication headers
    request.add_header("Authorization", "Bearer " + get_token())
    request.add_header("User-Agent", "")

    # deserialize to python dict
    response = json.load(urllib.request.urlopen(request))

    # if artist does not exist
    if len(response["response"]["hits"]) == 0:
        return -1

    # grab id from dict
    return response["response"]["hits"][0]["result"]["primary_artist"]["id"]
    

def get_token():
    """ Opens the file that stores the api keys, returns the Genius APi access token """

    with open('./secrets.json') as secrets:
        return json.load(secrets).get("access_token")


def check_elem_exist(input):
    """ Takes in a html object and checks to see that it is valid """

    if input is None:
        return "NA"
    else:
        return input.get_text()


# run functions

# update_artist("Billy Woods")

# createDB("./db/geniusSQLite.db")

# clear_database()

# load_from_csv("./data/output/all.csv")
