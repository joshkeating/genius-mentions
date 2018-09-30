from bs4 import BeautifulSoup as bs
import requests
import csv
import re
import random
import time


def checkElementExistence(input):
    if input is None:
        return "NA"
    else:
        return input.get_text()



def processNRows(sourceFile, outputFile):

    sourceFilePath = "./data/output/" + sourceFile
    outputFilePath = "./data/output/" + outputFile

    # open input file
    csvfile =  open(sourceFilePath, newline='')
    reader = csv.reader(csvfile, delimiter=';', quotechar='|')

    # open file to write updated results 
    output = open(outputFilePath, 'w', newline='')
    writer = csv.writer(output, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)


    # add the header to the file
    writer.writerow(["song_id", "title", "title_with_featured", "primary_artist_id",
                     "primary_artist_name", "url", "album", "full_date", "date_month", "date_year", "lyrics"])

    count = 0

    # define the regex to replace metadata we dont care about
    pattern = r"\[.*\]|\(x[0-9]\)|\n"

    # skip the header
    next(reader)

    for currentRow in reader:

        try:

            # get data from file
            songId = currentRow[0]
            songTitle = currentRow[1]
            titleWithFeat = currentRow[2]
            primaryArtistId = currentRow[3]
            artist = currentRow[4]
            url = currentRow[5]

            targetPage = requests.get(url)
            html = bs(targetPage.text, "html.parser")


            dateMonth = "NA"
            dateYear = "NA"

            # get raw text from a couple of elements on the page
            lyricsStandard = checkElementExistence(html.find("div", class_="lyrics"))
            fullDate = checkElementExistence(html.find("span", class_="metadata_unit-info metadata_unit-info--text_only")) 
            album = checkElementExistence(html.find("a", class_="song_album-info-title")).strip()

            # process metadata
            if fullDate != "NA":
                splitDate = fullDate.split()
                dateMonth = splitDate[0]
                dateYear = splitDate[2]
                
            # remove annotations and extra spaces
            lyricsTemp = re.sub(pattern, " ", lyricsStandard)
            lyrics = re.sub(' +',' ',lyricsTemp)

            # write to file
            writer.writerow([songId, songTitle, titleWithFeat, primaryArtistId, artist, url, album, fullDate, dateMonth, dateYear, lyrics])
            count += 1

            # print status and sleep for random intervals
            if count % 20 == 0:
                print(str(count) + " records processed")
                waitTime = random.randint(4, 15)
                print("Waiting " + str(waitTime) + " seconds...")
                time.sleep(waitTime)
        
        except IndexError:
            print("Malformed html data")
        except:
            print("Something Broke!")

    return

        
# run it
processNRows("ao6.csv", "full-ao6.csv")




