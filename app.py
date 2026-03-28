from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    conn = sqlite3.connect('complaints.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  password TEXT)''')

    conn.execute('''CREATE TABLE IF NOT EXISTS complaints
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  issue TEXT,
                  status TEXT)''')
    conn.close()

init_db()

@app.route('/')
def home():
    return redirect('/login')

# 🔐 LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('complaints.db')
        data = conn.execute("SELECT * FROM users WHERE username=? AND password=?",(user,pwd)).fetchone()
        conn.close()

        if data:
            session['user'] = user
            return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template('login.html')

# 📝 REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('complaints.db')
        conn.execute("INSERT INTO users (username,password) VALUES (?,?)",(user,pwd))
        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html', user=session['user'])

# ➕ ADD COMPLAINT
@app.route('/add', methods=['GET','POST'])
def add():
    if request.method == 'POST':
        issue = request.form['issue']
        user = session['user']

        conn = sqlite3.connect('complaints.db')
        conn.execute("INSERT INTO complaints (user, issue, status) VALUES (?,?,?)",
                     (user, issue, "Pending"))
        conn.commit()
        conn.close()

        return redirect('/view')

    return render_template('add.html')

# 📋 VIEW
@app.route('/view')
def view():
    conn = sqlite3.connect('complaints.db')
    data = conn.execute("SELECT * FROM complaints").fetchall()
    conn.close()
    return render_template('view.html', data=data)

# ✅ UPDATE
@app.route('/update/<int:id>')
def update(id):
    conn = sqlite3.connect('complaints.db')
    conn.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/view')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)