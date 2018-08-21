# quick and dirty scraper of wikipedia list page
# requires a bit of post scrape data massageing

from bs4 import BeautifulSoup as bs
import requests
import re

target = requests.get("https://en.wikipedia.org/wiki/List_of_hip_hop_musicians")
soup = bs(target.text, "html.parser")
output = open('./data/artists-output.txt', 'w')

# the low hanging fruit
undesirables = [None, "Enlarge"]

# use the limit param for smaller output
for link in soup.find_all("a"):

    url = link.get("title")
    if url not in undesirables:
        output.write(url + '\n')

output.close()

