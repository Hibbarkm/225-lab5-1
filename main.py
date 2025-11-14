from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Use persistent NFS path to match Jenkins reset commands
DB_PATH = '/nfs/demo.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts")  # assuming you're now tracking parts
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_part():
    name = request.form['name']
    quantity = request.form['quantity']
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO parts (name, quantity) VALUES (?, ?)", (name, quantity))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_part(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM parts WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
