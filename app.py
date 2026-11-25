from flask import Flask, render_template, request, redirect, session
import sqlite3
app = Flask(__name__)
app.secret_key = "secret123"
import sqlite3
def get_db():
    return sqlite3.connect("asset.db")
con = get_db()
cur = con.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    cost INTEGER,
    status TEXT,
    assigned_to TEXT
)""")
cur.execute("INSERT OR IGNORE INTO users VALUES ('arun','1234','Employee')")
cur.execute("INSERT OR IGNORE INTO users VALUES ('priya','1234','Employee')")
cur.execute("INSERT OR IGNORE INTO users VALUES ('vicky','1234','Employee')")
con.commit()
con.close()
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if username and password:
            session['username'] = username
            session['role'] = role

            if role == "Admin":
                return redirect('/admin_dashboard')
            elif role == "Staff":
                return redirect('/staff_dashboard')
            elif role == "HR":
                return redirect('/hr_dashboard')
            elif role == "Employee":
                return redirect('/employee_dashboard')

    return render_template("login.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'Admin':
        return "Access Denied"
    return render_template("dashboard.html")

@app.route('/staff_dashboard')
def staff_dashboard():
    if session.get('role') != 'Staff':
        return "Access Denied"
    return render_template("dashboard.html")

@app.route('/hr_dashboard')
def hr_dashboard():
    if session.get('role') != 'HR':
        return "Access Denied"
    return render_template("dashboard.html")

@app.route('/employee_dashboard')
def employee_dashboard():
    if session.get('role') != 'Employee':
        return "Access Denied"
    return render_template("dashboard.html")

@app.route('/add', methods=['GET', 'POST'])
def add():
    if session.get('role') != 'Admin':
        return "Access Denied"

    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        cost = request.form['cost']
        con = get_db()
        cur = con.cursor()
        cur.execute("INSERT INTO assets (name, category, cost, status, assigned_to) VALUES (?, ?, ?, 'Available', '')",
                    (name, category, cost))
        con.commit()
        con.close()
        return redirect('/view')
    return render_template("add_asset.html")

@app.route('/view')
def view():
    con = get_db()
    cur = con.cursor()
    search = request.args.get('search')
    if search:
        cur.execute("SELECT * FROM assets WHERE name LIKE ?", ('%' + search + '%',))
    else:
        cur.execute("SELECT * FROM assets")
    data = cur.fetchall()
    return render_template("view_asset.html", assets=data)

@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    status = request.form['status']
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE assets SET status=? WHERE id=?", (status, id))
    con.commit()
    con.close()
    return redirect('/view')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    con = get_db()
    cur = con.cursor()
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        cost = request.form['cost']
        cur.execute("UPDATE assets SET name=?, category=?, cost=? WHERE id=?",
                    (name, category, cost, id))
        con.commit()
        con.close()
        return redirect('/view')
    cur.execute("SELECT * FROM assets WHERE id=?", (id,))
    asset = cur.fetchone()
    return render_template("edit_asset.html", asset=asset)


@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'Admin':
        return "Access Denied"
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM assets WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect('/view')


@app.route('/assign/<int:id>', methods=['POST'])
def assign(id):
    if session.get('role') != 'HR':
        return "Access Denied"
    employee = request.form['employee']
    con = get_db()
    cur = con.cursor()
    cur.execute("UPDATE assets SET status='Allocated', assigned_to=? WHERE id=?",
                (employee, id))
    con.commit()
    con.close()
    return redirect('/view')


@app.route('/my_assets')
def my_assets():
    if session.get('role') != 'Employee':
        return "Access Denied"
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM assets WHERE assigned_to=?", (session['username'],))
    data = cur.fetchall()
    return render_template("my_assets.html", assets=data)


@app.route('/report')
def report():
    if session.get('role') not in ['Admin','HR']:
        return "Access Denied"
    con = get_db()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM assets")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM assets WHERE status='Available'")
    available = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM assets WHERE status='Allocated'")
    allocated = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM assets WHERE status='Maintenance'")
    maintenance = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM assets WHERE status='Retired'")
    retired = cur.fetchone()[0]
    con.close()

    return render_template("report.html",
                           total=total,
                           available=available,
                           allocated=allocated,
                           maintenance=maintenance,
                           retired=retired)
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)