import sqlite3
from sqlite3 import Error
import re
from datetime import datetime
import pandas as pd
import numpy as np

from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource, HoverTool, PanTool, BoxZoomTool, WheelZoomTool, ResetTool, SaveTool
from bokeh.palettes import *
from bokeh.transform import factor_cmap, jitter



def search_mention(lyrics, target_word):
    """ 
    Takes in a lyrics string and a target word, returns a count of the number of times the target
    word occurs in the lyric string
    """

    return sum(1 for n in re.finditer(r'\b%s\b' % re.escape(target_word), lyrics, flags=re.IGNORECASE))


def convert_to_datetime(input_string):
    """
    docstring
    """

    if re.match(r'[a-zA-Z]+ [0-9]+, \d{4}', input_string):
        return datetime.strptime(input_string, '%B %d, %Y')
    else:
        return None


    

def month_plot(target_word):
    """
    docstring
    """

    print("searching for " + target_word)

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date, S.lyrics
                        FROM songs AS S, artists AS A
                        WHERE S.primary_artist_id = A.artist_id'''

    # this might be bad for performance in the long run
    full_df = pd.read_sql_query(query_string, conn)
    # add count of target word to df
    full_df['count'] = full_df['lyrics'].apply(search_mention, args=(target_word,))

    # convert date string to datetime object
    full_df['full_date'] = full_df['full_date'].apply(convert_to_datetime)

    # print(full_df.head())
    # print(list(full_df))
    # print(full_df['full_date'])

    return



month_plot("patek")