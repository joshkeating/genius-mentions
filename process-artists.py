from bs4 import BeautifulSoup as bs
import requests
import re
import json
import urllib.request

# get access tokens from file
with open('./secrets.json') as secrets:
    secretKeys = json.load(secrets)


targetArtist = "21 Savage"

token = secretKeys["access_token"]


# print(token)


host = "https://api.genius.com/search?q="

query = host + urllib.request.quote(targetArtist)
request = urllib.request.Request(query)

request.add_header("Authorization", "Bearer " + token)
request.add_header("User-Agent", "")


response = json.load(urllib.request.urlopen(request))

# give a big json obj of the artist
print(response)




