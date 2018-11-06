import sqlite3
import pandas as pd


def get_artist(artist):
    """
    Takes in the name of an artist and returns a dataframe of their songs in the database
    """

    print("searching for: \'" + artist + "\'")

    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date 
                      FROM songs AS S, artists AS A 
                      WHERE S.primary_artist_id = A.artist_id AND A.artist_name="{name}"'''.format(name = artist)

    # load sql query into pandas dateframe
    df = pd.read_sql_query(query_string, get_connection())

    print(df)
    return


def get_all_artists():
    """Prints a dataframe of all artists and their IDs."""

    query_string = '''SELECT  A.artist_id, A.artist_name
                      FROM artists AS A'''

    # load sql query into pandas dateframe
    df = pd.read_sql_query(query_string, get_connection())

    print(df)
    return


def get_connection():
    """returns a connection object to the sqlite database"""
    
    database_connection_string = "./db/geniusSQLite.db"
    return sqlite3.connect(database_connection_string)


def get_lyrics_for_song(song):
    """
    TODO
    """

    print("searching for: \'" + song + "\'")

    cursor = get_connection().cursor()
    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date, S.lyrics
                      FROM songs AS S, artists AS A
                      WHERE S.primary_artist_id = A.artist_id AND S.title="{name}"'''.format(name = song)

    cursor.execute(query_string)
    song_list = cursor.fetchall()

    for song in song_list:
        print('Song: ' + song[0])
        print('Artist: ' + song[1])
        print('Album: ' + song[2])
        print('Date: ' + song[3])
        print('Lryics: ' + song[4])
        print()

    return


get_artist("BROCKHAMPTON")
# get_lyrics_for_song("4r Da Squaw")