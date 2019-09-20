from flask import Flask, render_template, request, redirect
from flask_table import Table, Col
from PyDictionary import PyDictionary
import json
import time
import sys
import sqlite3 as sql
import random
from mw_get_def import ProcessWords

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/enternew', methods=['POST','GET'])
def new_term():
    if request.method == 'POST':
        if request.form['type']=="a":
            if request.form['term']=="":
                msg = "** Please enter a term to be defined, jackass. **"
            elif request.form['defin']=="":
                term = request.form['term']
                term_list = []
                term_list.append(term)
                ProcessWords(term_list)
                msg="Term Added."
            else:
                term = request.form['term']
                pos = request.form['pos']
                defin = request.form['defin']
                if defin:
                    con = sql.connect("vocab.db")
                    cur = con.cursor()
                    cur.execute("select max(id) from defined")
                    row = cur.fetchone()
                    next_id = int(row[0]) + 1
                    cur.execute("INSERT INTO defined (id, term,part_of_speech,definition, quizzed, correct2, date_added) VALUES (?,?,?,?,0,0,datetime(\"now\"))",
                            (next_id, term, pos, defin))
                    con.commit()
                    msg = "** Record for "+term+" as a " + pos + " successfully added to definition list. **"
                    con.close()
            return render_template('new_term2.html', msg=msg)
        elif request.form['type']=="b":
            dictionary=PyDictionary()
            undefs = []
            con = sql.connect('vocab.db')
            cur = con.cursor()
            term_list = request.form['term_list'].splitlines()
            ProcessWords(term_list)
            msg = "Second submit (B) returned"
            return render_template('new_term2.html', msg=msg)
        else:
            term_file = request.form["term_file"]
            msg = "Third submit (C) returned.  File was "+term_file
            word_list = open(term_file, 'r').read().splitlines()
            ProcessWords(word_list)
            return render_template('new_term2.html', msg=msg)
    else:
        return render_template('new_term2.html')

        


@app.route('/editterm/<termid>/')
def edit_term(termid):
    con = sql.connect("vocab.db")
    cur = con.cursor()
    # termid = int(termid)
    cur.execute("select * from defined where id = ?", (termid,))
    row = cur.fetchone()
    #print(row, file=sys.stderr)
    term = row[1]
    pos = row[2]
    defin = row[3]
    return render_template('edit_term.html', termid=termid, term=term, pos=pos, defin=defin)

@app.route('/editnewterm/<term>/')
def edit_newterm(term):
    con = sql.connect("vocab.db")
    cur = con.cursor()
    #term = request.args.get("term")
    cur.execute("select max(id) from defined")
    row = cur.fetchone()
    next_id = int(row[0]) + 1
    cur.execute("insert into defined (id, term)values(?,?)", (next_id, term))
    con.commit()
    return render_template('edit_term.html', termid=next_id, term=term)

@app.route('/addrec', methods=['POST', 'GET'])
# @app.route('/addrec/<termid>/')
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
                next_id = int(row[0]) + 1
                cur.execute(
                    "INSERT INTO defined (id, term,part_of_speech,definition, quizzed, correct, date_added) VALUES (?,?,?,?,0,0,datetime(\"now\"))",
                    (next_id, term, pos, defin))
                con.commit()
                msg = "Record successfully added to definition list."
                con.commit()

        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()


@app.route('/reporting')
def reporting():
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("select round(sum(correct)*100.0/count(correct)*1.0,1), count(correct) from quizquestion")
    row = cur.fetchone();
    oall = str(row[0]) + "% correct on " + str(row[1]) + " questions."

    cur.execute(
        'select term, sum(correct) as cor, count(correct) as tot, sum(correct)*1.0/count(correct)*1.0 as pct from quizquestion, defined where term_id = id group by term having pct < 1.0 order by pct, tot desc')
    rows = cur.fetchall();
    con.close()
    return render_template("reporting.html", oall=oall, rows=rows)


@app.route('/editrec', methods=['POST', 'GET'])
def editrec():
    msg = "1=1"
    termid = request.form['termid']
    term = request.form['term']
    pos = request.form['pos']
    defin = request.form['defin']
    con = sql.connect("vocab.db")
    cur = con.cursor()
    cur.execute("Update defined set definition = ?, term = ?, part_of_speech = ? WHERE id = ?", (defin, term, pos, termid))
    con.commit()
    msg = "Definition successfully updated"
    return render_template("result.html", msg=msg)
    con.close()

@app.route('/defined', methods=['POST','GET'])
@app.route('/defined/<alpha>')
def deflist(alpha=None):
    con = sql.connect("vocab.db")
    con.row_factory = sql.Row
    cur = con.cursor()

    if (alpha is None):
        if request.method == 'POST':
            srch_term = request.form['srch_term']
            qry = "select * from defined where term like('%"
            qry = qry + srch_term + "%') order by term"
            cur.execute(qry)
        else:
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


@app.route('/quiz', defaults={'nq': 10}, methods=['POST', 'GET'])
@app.route('/quiz/<nq>/', methods=['POST', 'GET'])
def quiz(nq):
    if request.method == 'GET':
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
            new_favor_factor = cur.execute("select favor_new from config")
            new_favor_factor = new_favor_factor.fetchone()[0]

            if random.randint(1, 100) < new_favor_factor:
                ## get all term ids that are not in quizquestions
                x = "select * from defined where id  not in (select distinct term_id from quizquestion) order by random() limit 1"
            else:
                got_wrong_factor = cur.execute("select favor_wrong from config")
                got_wrong_factor = got_wrong_factor.fetchone()[0]

                if random.randint(1, 100) > got_wrong_factor:
                    x = "select * from defined where id in (select distinct term_id from quizquestion) order by random() limit 1"
                else:
                    x = "select * from defined where id in (select term_id from quizquestion group by term_id having sum(correct)/count(correct)< 1) order by random() limit 1"
            cur.execute(x)
            row = cur.fetchone()
            termid = str(row["id"])
            term = str(row["term"])
            pos = str(row["part_of_speech"])
            correct = (str(row["definition"]).capitalize())
            #print(termid, term, pos, correct)

            ## Get distractors
            cur.execute(
                "select definition, id from defined where id != ? and part_of_speech = ? order by random() limit 3",
                (termid, pos))
            rows = cur.fetchall()
            options = {correct: 1}
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
            x.append(termid)
            quizd[(term)] = x
        #print(quizd)
        return render_template("quiz.html", quizd=quizd, quiz_id=quiz_id)
    else:
        #print(request.form)
        quiz_id = request.form['quiz_id']
        con = sql.connect("vocab.db")
        con.row_factory = sql.Row
        cur = con.cursor()
        for x in request.form:
            if x != 'quiz_id':
                if request.form[x] == 'NULL':
                    cur.execute("insert into quizquestion(quiz_id, term_id, correct) values(?,?,1)", (quiz_id, x))
                    con.commit()
                else:
                    cur.execute("insert into quizquestion(quiz_id, term_id, correct, guess) values(?,?,0,?)", (quiz_id, x, request.form[x]))
                    con.commit()
        cur.execute("select defined.id, term from defined, quizquestion where defined.id = quizquestion.term_id and quiz_id = ? and quizquestion.correct = 1 order by term", (quiz_id,))
        rows_r = cur.fetchall()
        nr = len(rows_r)
        cur.execute("select defined.id, term, defined.definition, guess from defined, quizquestion where defined.id = quizquestion.term_id and quiz_id = ? and quizquestion.correct = 0 order by term", (quiz_id,))
        rows_w = cur.fetchall()
        nw = len(rows_w)
        pct_r = round(nr*100/(nr + nw))
        return render_template("quiz_results.html", rows_r = rows_r, rows_w = rows_w, quiz_id = quiz_id, pct_r = pct_r)


@app.route('/del_udef', methods=['POST', 'GET'])
@app.route('/del_udef', methods=['POST', 'GET'])
def delete_udef():
    term = request.args.get("term")
    con = sql.connect("vocab.db")
    cur = con.cursor()
    cur.execute("delete from undefined where term = ?", (term,))
    con.commit()
    return udeflist()

@app.route('/del_def', methods=['POST', 'GET'])
def delete_term():
    termid = request.args.get("termid")
    con = sql.connect("vocab.db")
    cur = con.cursor()
    cur.execute("delete from defined where id = ?", (termid,))
    con.commit()
    return deflist()

if __name__ == '__main__':
    app.run(debug=True)


