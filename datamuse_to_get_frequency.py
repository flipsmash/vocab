import requests
import json
import sqlite3 as sql
import time, re

def Frequency(word):
    """ Gets frequency of word from whatever corpus datamuse uses """
    base = "http://api.datamuse.com/words?sp="
    word = word.lower()
    url = "http://api.datamuse.com/words?sp=" + word.lower() + '&md=f'
    r = requests.get(url)
    result = format(r.status_code)
    if result=="200":
        dict = r.json()
        if dict:
            word_datamuse =dict[0]['word']
            if word_datamuse == word:
                frequency = dict[0]['tags'][0]
                frequency = float(re.sub("^f:","", frequency))
                return frequency
            return None
        return None
    else:
        return None
