import sqlite3
con = sqlite3.connect('./db.db', check_same_thread=False)

problem_table = "create table if not exists problem (id integer primary key autoincrement, problem string, example string, score float);"
sub_problem_table = "create table if not exists sub_problem (id integer primary key autoincrement, problem_id int, sub_problem_id int, problem string, answer string, score float);"
submit_table = "create table if not exists submit (id integer primary key autoincrement, submit_id string, problem_id int, sub_problem_id int, answer string, explanation string, evaluation string, score float);"
objection_table = "create table if not exists objection (id integer primary key autoincrement, content string, problem_id int, sub_problem_id int, score float, result string);"

submit_table_delete = "drop table submit;"

def create_table():
    cur = con.cursor()
    cur.execute(problem_table)
    cur.execute(sub_problem_table)
    #cur.execute(submit_table_delete)
    cur.execute(submit_table)
    cur.execute(objection_table)

def insert_problem(problem, example, score, sub_problem):
    sc = 0
    for p in sub_problem:
        sc += p["score"]
    cur = con.cursor()
    cur.execute("insert into problem (problem, example, score) values (?, ?, ?)", (problem, example, sc))
    problem_id = cur.lastrowid
    cnt = 1
    for p in sub_problem:
        cur.execute("insert into sub_problem (problem_id, sub_problem_id, problem, answer, score) values (?, ?, ?, ?, ?)", (problem_id, cnt, p["problem"], p["answer"], p["score"]))
        cnt += 1
    con.commit()
    res = cur.execute("select * from problem")
    return problem_id

def find_problem_with_id(id):
    cur = con.cursor()
    problem = cur.execute("select * from problem where id = ?", (id, )).fetchall()[0]
    sub_problem = cur.execute("select * from sub_problem where problem_id = ?", (int(id),)).fetchall()
    temp = []
    for i in sub_problem:
        temp.append({
            "problem_id": i[1],
            "sub_problem_id": i[2],
            "problem": i[3],
            "answer": i[4],
            "score": int(i[5])
        })
    return {
        "id": problem[0],
        "problem": problem[1],
        "example": problem[2],
        "score": int(problem[3]),
        "sub_problem": temp
    }

def get_random_id():
    import random
    s = "abcdefghijklmnopqrstuvwxyz0123456789"
    r = ""
    for i in range(20):
        r += s[random.randrange(0, len(s))]
    return r

def insert_submit(result, answer, problem_id):
    submit_id = get_random_id()
    cur = con.cursor()
    idx = 0
    for i in result:
        cur.execute("insert into submit (problem_id, sub_problem_id, answer, submit_id, explanation, evaluation, score) values (?, ?, ?, ?, ?, ?, ?)", (problem_id, idx + 1, answer[idx], submit_id, i["explanation"], i["evaluation"], i["score"]))
        idx += 1
    con.commit()
    return submit_id

def find_all_problem():
    cur = con.cursor()
    submit = cur.execute("select * from problem").fetchall()
    ret = []
    for i in submit:
        ret.append({
            "problem_id": i[0]
        })
    return ret

def find_submit_with_submit_id(submit_id):
    cur = con.cursor()
    submit = cur.execute("select * from submit where submit_id = ?", (submit_id, )).fetchall()
    problem_id = submit[0][2]
    problem = cur.execute("select * from problem where id = ?", (problem_id, )).fetchall()[0]
    sub_problem = cur.execute("select * from sub_problem where problem_id = ?", (problem_id,)).fetchall()

    score = 0
    p = []
    for i in range(len(sub_problem)):
        st = submit[i]
        sp = sub_problem[i]
        score += st[7]
        p.append({
            "student_score": st[7],
            "student_answer": st[4],
            "explanation": st[5],
            "evaluation": st[6],
            "answer": sp[4],
            "score": int(sp[5]),
            "sub_problem_id": sp[2],
            "problem": sp[3]
        })

    return {
        "problem_id": problem[0],
        "problem": problem[1],
        "example": problem[2],
        "score": int(problem[3]),
        "student_score": score,
        "sub_problem": p
    }

def find_all_submit():
    cur = con.cursor()
    submit = cur.execute("select * from submit").fetchall()
    submit_id = {}
    for i in submit:
        if i[1] in submit_id:
            submit_id[i[1]]["student_score"] += i[7]
        else:
            problem = cur.execute("select * from problem where id = ?", (int(i[2]), )).fetchall()[0]
            submit_id[i[1]] = {
                "problem_id": problem[0],
                "score": problem[3],
                "student_score": i[7]
            }

    ret = []
    for i in submit_id:
        temp = submit_id[i]
        temp["submit_id"] = i
        temp["ratio"] = int(temp["student_score"] * 100 / temp["score"])
        ret.append(temp)
    return ret