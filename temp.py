import sqlite3 as sql
import random
con = sql.connect("vocab.db")
con.row_factory = sql.Row
cur = con.cursor()
cur.execute("select * from defined order by random() limit 1")
row = cur.fetchone();
term = str(row["term"])
pos = str(row["part_of_speech"])
correct = str(row["definition"])
cur.execute("select definition from defined where part_of_speech = ? order by random() limit 3", (pos,))
distractors = cur.fetchall();
answers = {"d1":distractors[0][0], "d2":distractors[1][0], "d3":distractors[2][0], "c":correct}
keys=list(answers.keys())
random.shuffle(keys)
defs=list()
for x in keys:
    defs.append(answers[x])
    
print(term)
print(pos)
print('\n')
print(defs)
print(keys)
