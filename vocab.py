from PyDictionary import PyDictionary
import json
import sqlite3
con = sqlite3.connect('vocab.db')
cur = con.cursor()
dictionary=PyDictionary()
term_list = open('vocab.txt', 'r').read().splitlines()

dicdic={}
undefs = []

for s in term_list:
    word = str(s.upper())
    definition = dictionary.meaning(word)
    
    try:
        for key in definition:
            #print(word, "as a", key, "means", definition[key])
            word=str(word)
            key = str(key)
            definit = str(definition[key])
            vals = (word, key, definit)
            cur.execute("select max(id) from defined")
            row = cur.fetchone()
            next_id = int(row[0])+1
            cur.execute("INSERT INTO defined (id, term, part_of_speech, definition) VAlUES (?,?,?,?)", (next_id, word, key, definit))
            cur.execute("delete from undefined where term = ?", (word))
    except:
          undefs.append(word)
          
#undefs = list(undefs)
for t in undefs:
    t = str(t.upper())
    try:
        con.execute("INSERT INTO undefined VALUES(?)", (t,))
    except con.IntegrityError:
        print("Term already present in the undefined table")
con.commit()
con.close()
print (undefs)
