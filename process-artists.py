from bs4 import BeautifulSoup as bs
import requests
import re
import json
import urllib.request
import csv
import time



# get access tokens from file
def getToken():
    with open('./secrets.json') as secrets:
        return json.load(secrets).get("access_token")


# comment
def getArtistData(artistId):

    # form query
    query = "https://api.genius.com/artists/" + str(artistId)
    request = urllib.request.Request(query)

    # add authentication headers
    request.add_header("Authorization", "Bearer " + getToken())
    request.add_header("User-Agent", "")

    # deserialize to python dict
    response = json.load(urllib.request.urlopen(request))

    return response


def getArtistId(artistName):

    # form query
    query = "https://api.genius.com/search?q=" + urllib.request.quote(artistName)
    request = urllib.request.Request(query)

    # add authentication headers
    request.add_header("Authorization", "Bearer " + getToken())
    request.add_header("User-Agent", "")

    # deserialize to python dict
    response = json.load(urllib.request.urlopen(request))

    # grab id from dict
    artistId = response["response"]["hits"][0]["result"]["primary_artist"]["id"]

    return artistId




def findAllSongsForArtist(artistName, output):

    # get the id of given artist
    artistId = getArtistId(artistName)

    currentPage = 1
    pageStatus = True
    recordsProcessed = 0
    
    # init output file
    # output = open(outputFile, 'w', newline='')
    writer = csv.writer(output, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)

    # process first call

    # form query
    query = "https://api.genius.com/artists/" + str(artistId) + "/songs?per_page=50&page=" + str(currentPage)
    request = urllib.request.Request(query)
    # add authentication headers
    request.add_header("Authorization", "Bearer " + getToken())
    request.add_header("User-Agent", "")
    # deserialize to python dict
    response = json.load(urllib.request.urlopen(request))

    songList = response.get("response").get("songs")

    for song in songList:

        songId = song.get("id")
        title = song.get("title")
        titleWithFeat = song.get("title_with_featured")
        url = song.get("url")
        primaryArtistId = song.get("primary_artist").get("id")
        primaryArtistName = song.get("primary_artist").get("name")
        # write to file
        writer.writerow([songId, title, titleWithFeat, primaryArtistId, primaryArtistName, url])
        recordsProcessed += 1

    print("Batch processed...", recordsProcessed, "records proccesed", sep=" ")
    time.sleep(5)

    # check to see if any more records exist
    if response["response"]["next_page"] == None:
        print("End of pages reached, Exiting")
        pageStatus = False
        # output.close()
            

    while pageStatus == True:

        currentPage += 1

        try:
            query = "https://api.genius.com/artists/" + str(artistId) + "/songs?per_page=50&page=" + str(currentPage)
            request = urllib.request.Request(query)
            # add authentication headers
            request.add_header("Authorization", "Bearer " + getToken())
            request.add_header("User-Agent", "")
            # deserialize to python dict
            response = json.load(urllib.request.urlopen(request))

            songList = response.get("response").get("songs")

            for song in songList:

                songId = song.get("id")
                title = song.get("title")
                titleWithFeat = song.get("title_with_featured")
                url = song.get("url")
                primaryArtistId = song.get("primary_artist").get("id")
                primaryArtistName = song.get("primary_artist").get("name")
                # write to file
                writer.writerow([songId, title, titleWithFeat, primaryArtistId, primaryArtistName, url])
                recordsProcessed += 1

            print("Batch processed...", recordsProcessed, "records proccesed", sep=" ")
            # Wait
            time.sleep(5)
            
            if response["response"]["next_page"] == None:
                print("End of pages reached, Exiting")
                pageStatus = False
                # output.close()

        except:
            print("Something broke!")

    print()
    print("Done.")
    return




# given an artist name, create a csv with their name as the filename
# find their genius id, load all their songs into the csv


def processFile(sourceFile, outputFile):

    sourceFilePath = "./data/" + sourceFile
    outputFilePath = "./data/output/" + outputFile

    # init output file
    output = open(outputFilePath, 'w', newline='')
    writer = csv.writer(output, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    # add the header to the file
    writer.writerow(["song_id", "title", "title_with_featured", "primary_artist_id", "primary_artist_name", "url"])
    

    # get names from file
    file = open(sourceFilePath, "r")
    nameList = file.readlines()

    for name in nameList:

        print("---- Processing: " + name)
        findAllSongsForArtist(name, output)

    output.close()
    return



# run it
processFile("ao1.txt", "ao1.csv")