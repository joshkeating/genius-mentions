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


with open('./data/artist-dict.json', 'w') as ad:
    json.dump(response, ad)

hits = response['response']['hits']


for key in hits:
    resultDict = key.get("result")
    print("Title: " + resultDict.get("title") + " URL: " + resultDict.get("url"))



# give a big json obj of the artist
# print(response)




