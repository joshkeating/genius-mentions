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



def searchMention(lyrics, target_word):
    """ 
    Takes in a lyrics string and a target word, returns a count of the number of times the target
    word occurs in the lyric string
    """

    return sum(1 for n in re.finditer(r'\b%s\b' % re.escape(target_word), lyrics, flags=re.IGNORECASE))


def month_plot(target_word):
    """
    docstring
    """

    print("searching for " + target_word)

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    # this might be bad for performance in the long run
    full_df = pd.read_sql_query("SELECT * FROM songs AS S, artists AS A WHERE S.primary_artist_id = A.artist_id", conn)

    print(full_df.head())

    return



month_plot("word")