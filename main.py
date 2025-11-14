from flask import Flask, render_template, request, redirect, url_for, g, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "replace-this-in-prod")

DB_PATH = 'data/warehouse.db'  # KEEP THIS PATH (do not change)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            part_id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            location TEXT
        );
    """)
    db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.before_first_request
def before_first():
    init_db()

@app.route('/')
def index():
    db = get_db()
    cursor = db.execute("SELECT part_id, part_name, quantity, location FROM parts ORDER BY part_id DESC")
    parts = cursor.fetchall()
    return render_template('index.html', parts=parts)

@app.route('/add', methods=['GET', 'POST'])
def add_part():
    if request.method == 'POST':
        part_name = request.form.get('part_name', '').strip()
        quantity = request.form.get('quantity', '0').strip()
        location = request.form.get('location', '').strip()

        if not part_name:
            flash("Part name is required.", "error")
            return redirect(url_for('add_part'))

        try:
            quantity_value = int(quantity)
            if quantity_value < 0:
                raise ValueError
        except ValueError:
            flash("Quantity must be a non-negative integer.", "error")
            return redirect(url_for('add_part'))

        db = get_db()
        db.execute(
            "INSERT INTO parts (part_name, quantity, location) VALUES (?, ?, ?)",
            (part_name, quantity_value, location)
        )
        db.commit()
        flash(f"Added part '{part_name}'.", "success")
        return redirect(url_for('index'))

    # GET
    return render_template('add.html')

@app.route('/delete/<int:part_id>', methods=['POST'])
def delete_part(part_id):
    db = get_db()
    cur = db.execute("SELECT part_name FROM parts WHERE part_id = ?", (part_id,))
    row = cur.fetchone()
    if row:
        db.execute("DELETE FROM parts WHERE part_id = ?", (part_id,))
        db.commit()
        flash(f"Deleted part '{row['part_name']}'.", "success")
    else:
        flash("Part not found.", "error")
    return redirect(url_for('index'))

if __name__ == '__main__':
    # For local development only. In deployments your WSGI server will call the app.
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG', '0') == '1')
