from PyDictionary import PyDictionary
import json
import sqlite3
conn = sqlite3.connect('vocab.db')
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
            conn.execute("INSERT INTO defined (term, part_of_speech, definition) VAlUES (?,?,?)", vals)
    except:
          undefs.append(word)
          
#undefs = list(undefs)
for t in undefs:
    t = str(t.upper())
    try:
        conn.execute("INSERT INTO undefined VALUES(?)", (t,))
    except conn.IntegrityError:
        print("Term already present in the undefined table")
conn.commit()
conn.close()
print (undefs)
