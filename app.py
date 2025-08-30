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
                id integer primary key autoincrement,
                task text not null)''')
    conn.commit()
    conn.close()

init_db()   #run once at startup

@app.route("/")
def index():
        conn=get_db_connection()
        tasks=conn.execute("select * from tasks").fetchall()
        conn.close()
        return render_template("index.html",tasks=tasks)

@app.route("/add",methods=["POST"])
def add_task():
    task=request.form.get("task")
    if task:
        conn=get_db_connection()
        conn.execute("insert into tasks(task) values(?)",(task,))
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


if __name__=="__main__":
    app.run(debug=True)