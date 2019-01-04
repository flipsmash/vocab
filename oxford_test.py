import requests
import json
import sqlite3 as sql
import time

app_id = '741da96a'
app_key = '5f83749620ab5b89b6a70e315e6616a9'

term_list = open('vocab.txt', 'r').read().splitlines()
language = 'en'
con = sql.connect("vocab.db")
cur = con.cursor()
for s in term_list:
    s = s.upper()
    qry = ("select * from defined where term =  \"%s\"" % s)
    cur.execute(qry)
    row = cur.fetchone()
    if row is None:
        word_id = s
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
                ent4 = ent4.replace(";","")
                ent4 = ent4.replace("\"", "")
                ent4 = ent4.replace("'", "")
                #print(word_id,speech_type, ent4)
                try:
                    with sql.connect("vocab.db") as con:
                        cur = con.cursor()
                        word_id = word_id.upper()
                        #Get biggest ID for new entry
                        qry = ("select max(id) from defined")
                        cur.execute(qry)
                        row = cur.fetchone()
                        biggest_id = int(row[0])+1
                        qry = ("insert into defined values (%s, \"%s\",\"%s\",\"%s\",0,0, datetime(\"now\"))" %(biggest_id, word_id, speech_type, ent4 ))
                        print(qry)
                        cur.execute(qry)
                        con.commit()
                        msg = word_id + ": Definition successfully updated"
                except Exception as e:
                    con.rollback()
                    e = str(e)
                    #print(e)
                    msg=word_id + ": " + e
                print(msg)
                time.sleep(1.5)
        else:
            try:
                cur = con.cursor()
                word_id = word_id.upper()
                qry = ("insert into undefined values (\"%s\")" % (word_id))
                cur.execute(qry)
                con.commit()
                msg = word_id + ": successfully added to undefined list."
                print(msg)
            except Exception as e:
                print("Attempting to add \"%s\" to the undefined list generated the following error:" % (word_id))
                print(e)
    else:
        print("Word ", s, " is already listed in the defined table.")
x = input("press any key to continue:")


