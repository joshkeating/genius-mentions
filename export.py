import sqlite3
from sqlite3 import Error
import re
from datetime import datetime
import pandas as pd
import numpy as np
import json
from collections import defaultdict
import string
from collections import Counter
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
import itertools

def date_filter(input_string):
    if re.match(r'[a-zA-Z]+ [0-9]+, \d{4}', input_string):
        return True
    else:
        return False
    

def export_json_counts():

    database_connection_string = "./db/geniusSQLite.db"
    conn = sqlite3.connect(database_connection_string)

    query_string = '''SELECT S.full_date, S.lyrics FROM songs AS S'''

    df = pd.read_sql_query(query_string, conn)

    df = df[df['full_date'].apply(date_filter)]


    data_dict = defaultdict(list)

    for row in df.itertuples():
        
        cur_date = row.full_date

        cur_date = datetime.strptime(cur_date, '%B %d, %Y').date().isoformat()[:7]


        lyric_bulk = row.lyrics.lower()

        stop_words = set(stopwords.words('english'))
        stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}', '-'])

        split = [i for i in wordpunct_tokenize(lyric_bulk) if i not in stop_words]

        for word in split:

            if (word != ''):
                data_dict[word].append(cur_date)
            

    for key in data_dict:
        data_dict[key] = Counter(data_dict.get(key))

    # # chunk dict into parts
    # i = itertools.cycle(range(5))
    # split_dicts = [dict() for _ in range(5)]
    # for k, v in data_dict.items():
    #     split_dicts[next(i)][k] = v
    
    # # output files
    # for index, cDict in enumerate(split_dicts):

    #     filename = 'data-monthly' +  str(index) + '.json'
    #     with open(filename, 'w') as outfile:  
    #         json.dump(cDict, outfile)

    # testing
    with open('data-monthly.json', 'w') as outfile:
        json.dump(data_dict, outfile)

    return 


export_json_counts()


