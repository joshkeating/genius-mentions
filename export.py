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
        lyric_bulk = row.lyrics.lower()

        split = lyric_bulk.split(' ')

        for word in split:

            table = str.maketrans({key: None for key in string.punctuation})
            word = word.translate(table)  

            if (word != ''):
                data_dict[word].append(cur_date)
            

    for key in data_dict:
        data_dict[key] = Counter(data_dict.get(key))

    with open('data.json', 'w') as outfile:  
        json.dump(data_dict, outfile)

    return 


export_json_counts()


