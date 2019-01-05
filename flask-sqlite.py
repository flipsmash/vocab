from flask import Flask, render_template, request, redirect
import time
import sys
import sqlite3 as sql
import random

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/enternew', defaults={'termid': None})
@app.route('/enternew/<termid>/')
def new_term(termid):

    if termid is not None:
        print(termid, file=sys.stderr)
        print(type(termid))
        con = sql.connect("vocab.db")
        cur = con.cursor()
        #termid = int(termid)
        cur.execute("select * from defined where id = ?", termid)
        row = cur.fetchone()
        print(row, file=sys.stderr)
        print(type(row))
        return render_template('new_term.html', term=row)
    else:
        return render_template('new_term.html', term = "NULL")


@app.route('/addrec', methods=['POST', 'GET'])
#@app.route('/addrec/<termid>/')
def addrec():
    if request.method == 'POST':
        try:
            term = request.form['term']
            pos = request.form['pos']
            defin = request.form['defin']

            with sql.connect("vocab.db") as con:
                cur = con.cursor()
                cur.execute("select max(id) from defined")
                row = cur.fetchone()
                next_id = int(row[0])+1
                cur.execute("INSERT INTO defined (id, term,part_of_speech,definition, quizzed, correct, date_added) VALUES (?,?,?,?,0,0,datetime(\"now\"))", (next_id,term, pos, defin))
                con.commit()
                msg = "Record successfully added to definition list."
                con.commit()

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()



# @app.route('/quizproc', methods=['POST', 'GET'])
# def quizproc():
#     if request.method == 'POST':
#         try:
#             term = request.form['term']
#             pos = request.form['pos']
#             ans = request.form['ans']
#
#             with sql.connect("vocab.db") as con:
#                 cur = con.cursor()
#                 cur.execute("Update defined set quizzed = quizzed +1 WHERE term = ? and part_of_speech = ?",
#                             (term, pos))
#                 con.commit()
#                 if ans == 'c':
#                     msg = "Correct!"
#                     cur.execute("Update defined set correct = correct+1 WHERE term = ? and part_of_speech = ?",
#                                 (term, pos))
#                 else:
#                     msg = "Sorry, that is not correct"
#                 con.commit()
#         except:
#             con.rollback()
#             msg = "error in update operation"
#         finally:
#             con.close()
#             return msg


@app.route('/reporting')
def reporting():
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select round(sum(correct)*100.0/sum(quizzed)*1.0,1), cast(sum(quizzed) as integer) from defined")
    row = cur.fetchone();
    oall = str(row[0]) + "% correct on " + str(row[1]) + " questions."

    cur.execute(
        'select term, sum(correct) as cor, count(correct) as tot, sum(correct)*1.0/count(correct)*1.0 as pct from quizquestion group by term having pct < 1.0 order by pct, tot desc')
    rows = cur.fetchall();
    return render_template("reporting.html", oall=oall, rows=rows)
    con.close()


@app.route('/editrec', methods=['POST', 'GET'])
def editrec():
    if request.method == 'POST':
        try:
            term = request.form['term']
            pos = request.form['pos']
            defin = request.form['defin']

            with sql.connect("vocab.db") as con:
                cur = con.cursor()
                cur.execute("Update defined set definition = ? WHERE term = ? and part_of_speech = ?",
                            (defin, term, pos))

                con.commit()
                msg = "Definition successfully updated"

        except:
            con.rollback()
            msg = "error in update operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/defined')
@app.route('/defined/<alpha>')
def deflist(alpha=None):
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    if (alpha is None):
        cur.execute("select * from defined order by term")
    else:
        alpha = alpha + "%"
        qry = "select * from defined where term like('"
        qry = qry + alpha + "%') order by term"
        cur.execute(qry)

    rows = cur.fetchall()
    num_words = len(rows)
    return render_template("list.html", rows=rows, num_words=num_words)


@app.route('/undefined')
def udeflist():
    con = sql.connect("vocab.db")
    con.execute("delete from undefined where term IN(select distinct term from defined)")
    con.commit()
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from undefined order by term")

    rows = cur.fetchall();
    num_words = len(rows)
    return render_template("list2.html", rows=rows, num_words=num_words)


@app.route('/flashcard')
def flashcard():
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from defined order by random() limit 1")

    row = cur.fetchone()
    return render_template("cardfront.html", row=row)


@app.route('/edit', defaults={'term': "xxxxxxxxxx", 'pos': "xxxxxxxxxx"})
@app.route('/edit/<term>/<pos>/')
def edit(term, pos):
    if term != 'xxxxxxxxxx' and pos != 'xxxxxxxxxx':
        con = sql.connect("vocab.db")
        con.row_factory = sql.Row

        cur = con.cursor()
        cur.execute("select definition from defined where term = ? and part_of_speech = ?", (term, pos))

        row = cur.fetchone();
        defin = str(row["definition"])
        return render_template("edit_term.html", term=term, pos=pos, defin=defin)
    else:
        return deflist()


@app.route('/quiz', defaults={'nq': 10},  methods=['POST', 'GET'])
@app.route('/quiz/<nq>/',  methods=['POST', 'GET'])
def quiz(nq):
    if request.method == 'GET':
        nq=int(nq)
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
        
        return render_template("quiz.html", quizd = quizd)
    else:
##        return(request.form)
        print(request.form, file=sys.stderr)
        return("girlhomo")
@app.route('/del_udef', methods=['POST', 'GET'])
def delete_udef():
    return ("OK DOKEY SMKOEY!")


if __name__ == '__main__':
    app.run(debug=True)
