from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app= Flask(__name__)

#connect to database
def get_db_connection():
    conn=sqlite3.connect("todo.db")
    conn.row_factory=sqlite3.Row
    return conn

#initialize db
def init_db():
    conn=get_db_connection()
    conn.execute('''
                create table if not exists tasks(
                id INTEGER primary key autoincrement,
                task text not null,
                completed INTEGER DEFAULT 0,
                due_date text,
                priority INTEGER default 0
                )''')
    conn.commit()
    conn.close()

init_db()   #run once at startup

@app.route("/")
def index():

        search= request.args.get("search","")
        sort=request.args.get("sort","")

        conn=get_db_connection()
        query=" SELECT * FROM tasks "
        params=[]

        if search:
            query+=" where task like ? "
            params.append(f"%{search}%")

        if sort==" priority ":
            query+=" order by priority desc "
        elif sort==" due_date ":
            query+=" order by due_date asc "
        else:
            query+=" order by id desc "

        if params:
         tasks = conn.execute(query, params).fetchall()
        else:
         tasks = conn.execute(query).fetchall()
        conn.close()
        return render_template("index.html",tasks=tasks,search=search,sort=sort)

@app.route("/add",methods=["POST"])
def add_task():
    task=request.form.get("task")
    due_date=request.form.get("due_date")
    priority=request.form.get("priority")
    if task:
        conn=get_db_connection()
        conn.execute("insert into tasks(task,due_date,priority) values(?,?,?)",(task,due_date,priority))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    conn=get_db_connection()
    conn.execute("delete from tasks where id=?",(task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/edit/<int:task_id>")
def edit_task(task_id):
    conn=get_db_connection()
    task= conn.execute("select* from tasks where id=?",(task_id,)).fetchone()
    conn.close()
    return render_template("edit.html",task=task)

@app.route("/update/<int:task_id>",methods=["POST"])
def update_task(task_id):
    new_task=request.form.get("task")
    due_date=request.form.get("due_date")
    priority=request.form.get("priority")

    if new_task:
        conn=get_db_connection()
        conn.execute("update tasks set task=?,due_date=?,priority=? where id=?",(new_task,due_date,priority,task_id))
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):

    conn=get_db_connection()
    task=conn.execute("select completed from tasks where id=?",(task_id,)).fetchone()
    conn.close()

    if task:
        new_status=0 if task["completed"] else 1
        conn.execute("update tasks set completed=? where id=?",(new_status,task_id))
        conn.commit()

    return redirect(url_for("index"))


if __name__=="__main__":
    app.run(debug=True)