import csv
import re
from bokeh.plotting import figure, output_file, show


sourceFilePath = "./data/output/full-ao1.csv"

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

dateFormat = re.compile(r'\d{4}')


oc = []
dates = []

for currentRow in reader:

    # songTitle = currentRow[1]
    # artist = currentRow[4]

    year = currentRow[9]


    count = searchMention(currentRow[10], target)

    
    

    if count != 0 and dateFormat.match(year):
        oc.append(count)
        dates.append(year)

        # print(str(artist) + ",  " + str(songTitle) + ",  " + "occurrences:  " + str(count))
        # totalCount += count


# print(oc)
# print(dates)

# print()
# print(totalCount)
# print(first)

# what I want: 
# scatterplot with line, hoverable metadata



# output to static HTML file
output_file("./plots/lines.html")

# create a new plot with a title and axis labels
p = figure(title="title", x_axis_label='years', y_axis_label='counts')

# add a line renderer with legend and line thickness
p.circle(dates, oc, fill_alpha=0.2, size=oc, legend="Temp.")

# show the results
show(p)