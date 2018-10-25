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
    Given a input string, attempts to convert it into a datetime object. If the input string does not 
    match the expected pattern, return None
    """

    if re.match(r'[a-zA-Z]+ [0-9]+, \d{4}', input_string):
        return datetime.strptime(input_string, '%B %d, %Y')
    else:
        return None


def month_plot_line(target_word):
    """
    Takes in a target word in the form of a string, plots the occurences of that string over history
    """

    print("searching for: \'" + target_word + "\'")

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date, S.lyrics
                        FROM songs AS S, artists AS A
                        WHERE S.primary_artist_id = A.artist_id'''

    # this might be bad for performance in the long run
    df = pd.read_sql_query(query_string, conn)
    # add count of target word to df
    df['count'] = df['lyrics'].apply(search_mention, args=(target_word,))

    # convert date string to datetime object
    df['full_date'] = df['full_date'].apply(convert_to_datetime)

    # drop nulls
    df= df.dropna(subset=['full_date'])

    # set index and filter bad data
    df = df.set_index('full_date')
    df.index = pd.to_datetime(df.index, errors='coerce', infer_datetime_format=True)

    # resample to monthly bins
    mo_downsampled = df.resample('M').sum()

    # remove zero counts
    mo_downsampled = mo_downsampled[mo_downsampled["count"] > 0]

    
    # ---- Plot Code ---- #

    # output to static HTML file
    output_file("./plots/month-counts.html")
    
    # palette = viridis(len(artists)) #pylint: disable=E0602
    
    source_sum = ColumnDataSource(mo_downsampled)

    # define behavior for hover
    hover = HoverTool(
        tooltips=[('Sum', '@count'), ('Date', '@full_date{%B %Y}')],
        formatters={
            'full_date' : 'datetime', # use 'datetime' formatter for 'dates' field
        }
    )

    title = "\'" + target_word + "\' References Over Time"

    monthly_counts = figure(title=title,
                            x_axis_label='Time', 
                            y_axis_label='Counts', 
                            x_axis_type="datetime",
                            tools=[
                                hover, PanTool(), BoxZoomTool(), 
                                WheelZoomTool(), ResetTool(), SaveTool()
                            ]
                           )
    monthly_counts.line(x='full_date', y='count', source=source_sum, line_width=2.5, legend="Monthly Sum")

    monthly_counts.circle(x="full_date", y="count", size=8, hover_color="red", source=source_sum)

    show(monthly_counts)

    return
    

def artist_plot_scatter(target_word):
    """
    Takes in a target word in the form of a string, plots the occurences of that string over history
    """

    print("searching for: \'" + target_word + "\'")

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.title, A.artist_name, S.album, S.full_date, S.lyrics
                        FROM songs AS S, artists AS A
                        WHERE S.primary_artist_id = A.artist_id'''

    # this might be bad for performance in the long run
    df = pd.read_sql_query(query_string, conn)
    # add count of target word to df
    df['count'] = df['lyrics'].apply(search_mention, args=(target_word,))

    # convert date string to datetime object
    df['full_date'] = df['full_date'].apply(convert_to_datetime)

    # drop nulls
    df= df.dropna(subset=['full_date'])

    # set index and filter bad data
    df = df.set_index('full_date')
    df.index = pd.to_datetime(df.index, errors='coerce', infer_datetime_format=True)

    # remove zero counts
    df = df[df["count"] > 0]


    # ---- Plot Code ---- #

    # output to static HTML file
    output_file("./plots/artist-scatter.html")
    
    palette = viridis(len(df['artist_name'])) #pylint: disable=E0602
    
    source = ColumnDataSource(df)

    # define behavior for hover
    hover = HoverTool(
        tooltips=[('Artist', '@artist_name'), ('Title', '@title'),('Album', '@album'), 
                  ('Sum', '@count'), ('Date', '@full_date{%B %Y}')],
        formatters={
            'full_date' : 'datetime', # use 'datetime' formatter for 'dates' field
        }
    )

    title = "\'" + target_word + "\' References Over Time"

    scatter_plot = figure(title=title,
                            x_axis_label='Time',
                            y_axis_label='Counts', 
                            x_axis_type="datetime",
                            tools=[
                                hover, PanTool(), BoxZoomTool(), 
                                WheelZoomTool(), ResetTool(), SaveTool()
                            ]
                        )

    scatter_plot.circle(x='full_date', y='count', fill_alpha=0.4, size=8, source=source,
        fill_color=factor_cmap('artist_name', palette=palette, factors=df.artist_name))

    show(scatter_plot)

    return


def artist_word_scatter(target_word, artist):
    """
    Takes in a target word and artist name and plots a scatterplot of the number of times
    that artist used a word in their songs
    """

    print("searching for: \'" + target_word + "\'")

    # database location
    database_connection_string = "./db/geniusSQLite.db"

    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.title, A.artist_name, S.album, S.lyrics, S.full_date 
                      FROM songs AS S, artists AS A 
                      WHERE S.primary_artist_id = A.artist_id AND A.artist_name="{name}"'''.format(name = artist)

    # this might be bad for performance in the long run
    df = pd.read_sql_query(query_string, conn)
    # add count of target word to df
    df['count'] = df['lyrics'].apply(search_mention, args=(target_word,))

    # convert date string to datetime object
    df['full_date'] = df['full_date'].apply(convert_to_datetime)

    # drop nulls
    df= df.dropna(subset=['full_date'])

    # set index and filter bad data
    df = df.set_index('full_date')
    df.index = pd.to_datetime(df.index, errors='coerce', infer_datetime_format=True)

    # remove zero counts
    df = df[df["count"] > 0]

    print("Total uses of " + target_word + ": " + str(df['count'].sum()))


    # ---- Plot Code ---- #

    # output to static HTML file
    output_file("./plots/artist-scatter.html")
    
    palette = viridis(len(df['artist_name'])) #pylint: disable=E0602
    
    source = ColumnDataSource(df)

    # define behavior for hover
    hover = HoverTool(
        tooltips=[('Artist', '@artist_name'), ('Title', '@title'),
            ('Album', '@album'), ('Sum', '@count'), ('Date', '@full_date{%B %Y}')],
        formatters={
            'full_date' : 'datetime', # use 'datetime' formatter for 'dates' field
        }
    )

    title = "\'" + target_word + "\' References Over Time"

    scatter_plot = figure(title=title,
                            x_axis_label='Time',
                            y_axis_label='Counts', 
                            x_axis_type="datetime",
                            tools=[
                                hover, PanTool(), BoxZoomTool(), 
                                WheelZoomTool(), ResetTool(), SaveTool()
                            ]
                        )

    scatter_plot.circle(x='full_date', y='count', fill_alpha=0.4, size=8, source=source,
        fill_color=factor_cmap('artist_name', palette=palette, factors=df.artist_name))

    show(scatter_plot)

    return



# month_plot_line("patek")

artist_plot_scatter("skrt")

