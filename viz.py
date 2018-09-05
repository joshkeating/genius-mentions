import csv
import re
from bokeh.plotting import figure, output_file, show
from datetime import datetime


from bokeh.models import ColumnDataSource
from bokeh.palettes import *
from bokeh.transform import factor_cmap, jitter

import pandas as pd
import numpy as np

sourceFilePath = "./data/output/all.csv"

# open input file
csvfile =  open(sourceFilePath, newline='')
reader = csv.reader(csvfile, delimiter=';', quotechar='|')

# skip header
next(reader)

# def search term
target = "patek"

totalCount = 0

def searchMention(lyrics, target):
    count = sum(1 for n in re.finditer(r'\b%s\b' % re.escape(target), lyrics, flags=re.IGNORECASE))
    return count

print("searching for " + target)

dateFormat = re.compile(r'[a-zA-Z]+ [0-9]+, \d{4}')


refCounts = []
dates = []
artists = []
titles = []

for currentRow in reader:

    curSongTitle = currentRow[1]
    curArtist = currentRow[4]
    curDateRaw = currentRow[7]
    curRefCount = searchMention(currentRow[10], target)

    if curRefCount != 0 and curRefCount < 30 and dateFormat.match(curDateRaw):
        # convert date string to datetime obj
        formattedDate = datetime.strptime(curDateRaw, '%B %d, %Y')
        # add values to lists
        artists.append(curArtist)
        titles.append(curSongTitle)
        refCounts.append(curRefCount)
        dates.append(formattedDate)

        # print(str(curArtist) + ", " + str(curSongTitle) + ", " + str(curRefCount) + ", " +  str(formattedDate))




artistsSeries = pd.Series(artists)
titlesSeries = pd.Series(titles)
datesSeries = pd.Series(dates)
countsSeries = pd.Series(refCounts)

data = {'artists' : artistsSeries,
        'titles' : titlesSeries,
        'dates' : datesSeries,
        'counts' : countsSeries
        }

genIndex = list(range(0, len(dates)))

df = pd.DataFrame(data)
df = df.set_index([genIndex, 'dates'])

# df of just monthly sums
monthDownsampled_Sum = df.resample('M', level=1).sum()

monthDownsampled_Avg = df.resample('M', level=1).mean()



# print(df.head())

# print(monthDownsampled)



# print(len(refCounts))
# print(len(dates))

# print(artists)

# print(len(dates))
# print(len(set(dates)))


# print()
# print(totalCount)
# print(first)





# genPal = viridis(len(artists)) #pylint: disable=E0602

# output to static HTML file
output_file("./plots/lines.html")

# # # code for scatter
# source1 = ColumnDataSource(data=dict(dates=dates, counts=refCounts, colors=artists))
# p = figure(title="title", x_axis_label='time', y_axis_label='counts', x_axis_type="datetime")
# p.circle(x='dates', y='counts', fill_alpha=0.6, size=10, source=source1, fill_color=factor_cmap('colors', palette=genPal, factors=artists))

# # show results
# show(p)


sourceSum = ColumnDataSource(monthDownsampled_Sum)
sourceAvg = ColumnDataSource(monthDownsampled_Avg)
monthlyCounts = figure(title="Patek References Over Time", x_axis_label='time', y_axis_label='counts', x_axis_type="datetime")
monthlyCounts.line(x='dates', y='counts', source=sourceSum, line_width=3, legend="Sum")
monthlyCounts.line(x='dates', y='counts', source=sourceAvg, line_width=3, legend="Avg")


show(monthlyCounts)




# jitter('counts', width=0.6, range=p.y_range)


# p.vbar_stack(artists, x='dates', width=0.9, color='colors', source=source1)

# source2 = ColumnDataSource(data=dict(dates=dates, counts=refCounts, colors=artists))
# p2 = figure(title="title", x_axis_type="datetime")
# p2.vbar(x='dates', top='counts', width=0.9, source=source2, fill_color=factor_cmap('colors', palette=genPal, factors=artists))

# pc = figure(x_axis_type="datetime", title="usage over time")
# pc.grid.grid_line_alpha=0.3
# pc.xaxis.axis_label = 'Date'
# pc.yaxis.axis_label = 'Count'
# pc.line(dates, cumulative, color='#A6CEE3', legend='patek')





# show(pc)