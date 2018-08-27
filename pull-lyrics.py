from bs4 import BeautifulSoup as bs
import requests
import csv
import re

# scrape for lyrics and metadata

csvfile =  open('./data/output/ao1.csv', newline='')
reader = csv.reader(csvfile, delimiter=';', quotechar='|')

i = 0
# move the iterator from the first line
next(reader)


pattern = r"\[.*\]|\(x[0-9]\)|\n"

while i < 2:

    currentRow = next(reader)

    songTitle = currentRow[1]
    artist = currentRow[4]
    url = currentRow[5]

    targetPage = requests.get(url)
    html = bs(targetPage.text, "html.parser")

    lyricsStandard = html.find("div", class_="lyrics").get_text()

    lyrics = re.sub(pattern, " ", lyricsStandard)

    print("Artist: " + artist)
    print("Song Title: " + songTitle)
    print(lyrics)
    print()

    i += 1


    

  

    

