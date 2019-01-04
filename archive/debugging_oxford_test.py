import requests
import json
import sqlite3 as sql
import time

app_id = '741da96a'
app_key = '5f83749620ab5b89b6a70e315e6616a9'

language = 'en'
word_id = 'destrier'
url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/definitions'
r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})
result = format(r.status_code)
if result=="200":
    dict = r.json()
    dict = dict['results'][0]
    dict = dict['lexicalEntries'] #dict is now list
    i=0
    for entry in dict:
        ent0 = (entry['entries']) #ent is list
        speech_type = (entry['lexicalCategory'])
        ent1 = ent0[0] #ent is dict again
        ent2 = ent1['senses'] #list
        ent3 = ent2[0] #dict
        ent4 = str(ent3['definitions'])
        ent4 = ent4.replace("['", "")
        ent4 = ent4.replace("']", "")
        ent4 = ent4.replace("[\"","")
        ent4 = ent4.replace("\"]","")
        print(word_id,speech_type, ent4)
        try:
            with sql.connect("vocab.db") as con:
                cur = con.cursor()
                word_id = word_id.upper()
                qry = ("insert into defined values (\"%s\",\"%s\",\"%s\",0,0)" %(speech_type, ent4, word_id))
                cur.execute(qry)    
                con.commit()
                msg = word_id + ": Definition successfully updated"
        except Exception as e: 
            con.rollback()
            e = str(e)
            #print(e)
            msg=word_id + ": " + e
        print(msg)
        
else:
    print(word_id+ " not found in Online OED (to do:) Moving to Undefined Words List")
time.sleep(1.5)

