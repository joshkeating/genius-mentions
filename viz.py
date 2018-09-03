import csv
import re
from bokeh.plotting import figure, output_file, show
from datetime import datetime


from bokeh.models import ColumnDataSource
from bokeh.palettes import *
from bokeh.transform import factor_cmap, jitter



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


oc = []
dates = []
artists = []

for currentRow in reader:

    # songTitle = currentRow[1]
    # artist = currentRow[4]

    dateRaw = currentRow[7]


    count = searchMention(currentRow[10], target)

    # dateFormat.match(year)

    if count != 0 and count < 30 and dateFormat.match(dateRaw):

        formattedDates = datetime.strptime(dateRaw, '%B %d, %Y')
        artists.append(currentRow[4])
        oc.append(count)
        dates.append(formattedDates)

        # print(str(artist) + ",  " + str(songTitle) + ",  " + "occurrences:  " + str(count))
        # totalCount += count


# print(len(oc))
# print(len(dates))

# print(artists)

# print(len(dates))
# print(len(set(dates)))

# print()
# print(totalCount)
# print(first)

# what I want: 
# scatterplot with line, hoverable metadata

genPal = viridis(len(artists)) #pylint: disable=E0602

# output to static HTML file
output_file("./plots/lines.html")

source1 = ColumnDataSource(data=dict(dates=dates, counts=oc, colors=artists))

# # create a new plot with a title and axis labels
p = figure(title="title", x_axis_label='time', y_axis_label='counts', x_axis_type="datetime")
p.circle(x='dates', y=jitter('counts', width=0.6, range=p.y_range), fill_alpha=0.6, size=10, source=source1, fill_color=factor_cmap('colors', palette=genPal, factors=artists))

# p.vbar_stack(artists, x='dates', width=0.9, color='colors', source=source1)

# source2 = ColumnDataSource(data=dict(dates=dates, counts=oc, colors=artists))
# p2 = figure(title="title", x_axis_type="datetime")
# p2.vbar(x='dates', top='counts', width=0.9, source=source2, fill_color=factor_cmap('colors', palette=genPal, factors=artists))



# p.line(dates, oc)

# show the results
# show(p)

show(p)