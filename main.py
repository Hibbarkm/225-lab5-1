from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecret"  # Needed for flash messages

# Persistent NFS database path
DB_PATH = '/nfs/demo.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM parts")
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add_part():
    part_name = request.form['part_name']
    quantity = request.form.get('quantity', 0)
    location = request.form.get('location', '')
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO parts (part_name, quantity, location) VALUES (?, ?, ?)",
        (part_name, quantity, location)
    )
    conn.commit()
    conn.close()
    flash(f"Added part '{part_name}'", "success")
    return redirect('/')

@app.route('/delete/<int:part_id>', methods=['POST'])
def delete_part(part_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM parts WHERE part_id=?", (part_id,))
    conn.commit()
    conn.close()
    flash(f"Deleted part ID {part_id}", "success")
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
