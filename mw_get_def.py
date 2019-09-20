from PyDictionary import PyDictionary
import requests
import json
import sqlite3 as sql
import time, re
from datamuse_to_get_frequency import Frequency

def WavMaintenance():
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select distinct term from defined order by term")
    rows = cur.fetchall()
    for row in rows:
        term = row['term']
        wav_url = Pronounce(term)
        if wav_url:
            cur.execute("update defined set wav_url = ? where term = ?", (wav_url, term))
            con.commit()
        print(term + ", " + str(wav_url))
    con.close()

def ProcessWords(term_list = []):
    app_key = '780b6f97-32cc-4573-a301-e6c8c325b67c'
    base = "https://www.dictionaryapi.com:443/api/v3/references/collegiate/json/"
    con = sql.connect("vocab.db")
    cur = con.cursor()
    for s in term_list:
        qry = ("select * from defined where term =  \"%s\"" % s)
        cur.execute(qry)
        row = cur.fetchone()
        if row is None:
            word_id = s
            url = base + word_id.lower() + '?key=' + app_key
            r = requests.get(url, headers = {'key':app_key})
            result = format(r.status_code)
            if result=="200":
                dict = r.json()
                try:
                    base_term = dict[0]['meta']['id']
                    base_term = re.sub(r":.*$","",base_term)
                    for entry in dict:

                        # Check if word is still word as opposed to the phrases M-W adds on too
                        term = entry['meta']['id']
                        term = re.sub(r":.*$","",term)
                        if term==base_term:
                            speech_type = entry["fl"]
                            
                            #ToDo: iterate through all shortdefs maybe given this is a list
                            definition = entry["shortdef"][0]
                            try:
                                with sql.connect("vocab.db") as con:
                                    cur = con.cursor()
                                    word_id = word_id.upper()
                                    #Get biggest ID for new entry
                                    qry = ("select max(id) from defined")
                                    cur.execute(qry)
                                    row = cur.fetchone()
                                    biggest_id = int(row[0])+1
                                    frequency = Frequency(term)
                                    wav_url = Pronounce(term)
                                    qry = ("insert into defined values (%s, \"%s\",\"%s\",\"%s\",0,0, datetime(\"now\"), %s, \"%s\")" %(biggest_id, term, speech_type, definition, frequency, wav_url ))
                                    print(qry)
                                    cur.execute(qry)
                                    con.commit()
                                    msg = word_id + ": Definition successfully updated from M-W"
                            except Exception as e:
                                con.rollback()
                                e = str(e)
                                #print(e)
                                msg=word_id + ": " + e
                            print(msg)
                            time.sleep(1.5)
                except:
                    print("No ID for given term foud in M-W (i.e. no matching word found")
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
                try:
                    ## try pydictionary to insert
                    definition = dictionary.meaning(word)
                    for key in definition:
                        word=str(word_id)
                        key = str(key)
                        definit = str(definition[key])
                        vals = (word, key, definit)
                        cur.execute("select max(id) from defined")
                        row = cur.fetchone()
                        next_id = int(row[0])+1
                        cur.execute("INSERT INTO defined (id, term, part_of_speech, definition) VAlUES (?,?,?,?, 0,0, datetime(\"now\"), NULL)", (next_id, word, key, definit))
                        #cur.execute("delete from undefined where term = ?", (word))
                        msg = word+" definition inserted into defined table via PyDictionary."
                        print(msg)
                except:
                    ## trying to insert into undefined
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
            print("Word ", s, " already exists in the defined table.")
    x = input("press any key to continue:")
    con.close()


###################
def Pronounce(term):
    term = term.lower()
    app_key = '780b6f97-32cc-4573-a301-e6c8c325b67c'
    base = "https://www.dictionaryapi.com:443/api/v3/references/collegiate/json/"
    url = base + term.lower() + '?key=' + app_key
    r = requests.get(url, headers = {'key':app_key})
    result = format(r.status_code)
    if result=="200":
        dict = r.json()
        try:
            base_url = "https://media.merriam-webster.com/soundc11/" + term[:1]+"/"
            base_file = dict[0]['hwi']['prs'][0]['sound']['audio']
            if base_file:
                base_url = base_url+base_file+".wav"
                return(base_url)
            else:
                return("1")            
        except:
            return ("1")
