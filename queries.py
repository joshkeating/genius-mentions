import sqlite3
import pandas as pd


def get_artist(artist):
    """
    Takes in the name of an artist and returns a dataframe of their songs in the database
    """

    print("searching for: \'" + artist + "\'")

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date 
                      FROM songs AS S, artists AS A 
                      WHERE S.primary_artist_id = A.artist_id AND A.artist_name="{name}"'''.format(name = artist)

    # this might be bad for performance in the long run
    df = pd.read_sql_query(query_string, conn)

    print(df)
    return





get_artist("Young Thug")