import sqlite3 as sql
import random

nq = input("Number of questions: ")
nq = int(nq)

con = sql.connect("vocab.db")
cur = con.cursor()
cur.execute("insert into quiz(q_num) values (?)", [nq])
quiz_id = cur.lastrowid
print(quiz_id)
con.commit()
cur.execute("select * from defined order by random() limit %s" % nq)
rows = cur.fetchall()
con.commit()
cur = con.cursor()
for x in range(len(rows)):
    # for x in range(0, len(rows)):
    ## instantiate a single question
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    # cur = con.cursor()
    # cur.execute("select * from defined order by random() limit 1")
    term = rows[x][2]
    print(term + ": ")
    pos = rows[x][0]
    correct = rows[x][1].capitalize()

    ## Get distractors
    cur.execute("select definition from defined where term!= ? and part_of_speech = ? order by random() limit 3",
                (term, pos))
    rows2 = cur.fetchall()
    options = {correct: 1}
    for i in range(0, 3):
        options[str(rows2[i][0])] = 0

    # shuffle
    keys = list(options.keys())
    random.shuffle(keys)
    x = [(key, options[key]) for key in keys]
    x = [list(i) for i in x]
    x[0].insert(0, 'A')
    x[1].insert(0, 'B')
    x[2].insert(0, 'C')
    x[3].insert(0, 'D')

    # output options
    for key in x:
        print(key[0], "-", key[1])
    ans = input("Letter: ")
    ans = ans.capitalize()
    ak = {"A": 0, "B": 1, "C": 2, "D": 3}
    choice: int = ak[ans]
    if x[choice][2] == 1:
        print('correct')
        cur = con.cursor()
        cur.execute('insert into quizquestion values(?,?,1,NULL)', (quiz_id, term))

    else:
        wrongdef = x[choice][1]
        print('wrong')
        cur = con.cursor()
        cur.execute('insert into quizquestion values(?,?,0,?)', (quiz_id, term, wrongdef))
    con.commit()
con.commit()
cur.execute('select sum(correct)*100 / count(term)  from quizquestion where quiz_id = %s' % quiz_id)
row = cur.fetchone()
print("You got", row[0], "percent correct.")
# to get update re words tested to date
# select term, sum(correct)*100/count(term) as percentage  from quizquestion group by term order by percentage;
con.commit()
cur.execute("select * from quizquestion where quiz_id = ? and correct = 0", [quiz_id])
rows3 = cur.fetchall()

keepopen = input("")
