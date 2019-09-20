import sqlite3 as sql
import random

nq = input("Number of questions: ")
nq = int(nq)

con = sql.connect("vocab.db")
cur = con.cursor()
cur.execute("insert into quiz(q_num) values (?)", [nq])
quiz_id = cur.lastrowid
con.commit()
quizd = {}
for z in range(nq):
    ## instantiate a single question
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    
    # favor words that have not yet been quizzed by a certain percentage
    new_favor_factor = 90
    if random.randint(1,100)< new_favor_factor:
        x = "select * from defined where term in (select term from defined except select distinct term from quizquestion) order by random() limit 1"
    else:
        got_wrong_factor = 90
        if random.randint(1,100) < got_wrong_factor:
            x = "select * from defined where term in (select distinct term from quizquestion) order by random() limit 1"
        else:
            x = "select * from defined where term in (select term from quizquestion group by term having sum(correct)/count(correct)< 1) order by random() limit 1"

    cur.execute(x)
    row = cur.fetchone()
    term = str(row["term"])
    pos = str(row["part_of_speech"])
    correct = (str(row["definition"]).capitalize())

    ## Get distractors
    cur.execute("select definition from defined where term!= ? and part_of_speech = ? order by random() limit 3",
                (term, pos))
    rows = cur.fetchall()
    options = {correct: 1}
    print(term)
    for i in range(0, 3):
        options[str(rows[i][0])] = 0

    # shuffle
    keys = list(options.keys())
    random.shuffle(keys)
    x = [(key, options[key]) for key in keys]
    x = [list(i) for i in x]
    x[0].insert(0, 'A')
    x[1].insert(0, 'B')
    x[2].insert(0, 'C')
    x[3].insert(0, 'D')
    quizd[term] = x
    # output options
    for key in x:
        print(key[0], "-", key[1])

    # get and check answer:
    ans = input("Letter: ")
    ans = ans.capitalize()
    ak = {"A": 0, "B": 1, "C": 2, "D": 3}
    choice: int = ak[ans]
    if x[choice][2] == 1:
        print('correct')
        cur.execute('insert into quizquestion values(?,?,1,NULL)', (quiz_id, term))
    else:
        wrongdef = x[choice][1]
        print('wrong')
        cur.execute('insert into quizquestion values(?,?,0,?)', (quiz_id, term, wrongdef))
    con.commit()
con.commit()

### Basic stats
##cur.execute('select sum(correct)*100 / count(term)  from quizquestion where quiz_id = %s' % quiz_id)
##row = cur.fetchone()
##print("You got", row[0], "percent correct.")
##
### to get update re words tested to date
##cur.execute('select term, count(term) as ct, sum(correct)*100/count(term) as percentage  from quizquestion group by term order by ct')
##rows = cur.fetchall();
##for row in rows:
##    print(row[0], row[1], row[2])
##
##hold = input("")

