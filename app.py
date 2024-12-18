from flask import Flask, render_template, request, session, flash, redirect, url_for
import sqlite3 as sql
import os

"""
Name:Donald Kremer
Date:11/14/24
Assignment:Module11:
Description: This assignment uses flask and html to assign role based 
    access to users.
Assumptions:NA
All work below was performed by Donald Kremer """

app = Flask(__name__)
app.secret_key = os.urandom(12)


def check_access(required_level):
    return session.get('logged_in') and session.get('security_level', 0) >= required_level

# Route for home page
@app.route('/')
def home():
    if not session.get("logged_in"):
        return redirect(url_for('login'))
    else:
        return render_template('home.html', name=session['name'])


# Route to display the form to add a new user
@app.route('/new_user')
def new_user():
    if not session.get('logged_in'):
        return render_template('login.html')
    elif session.get('admin'):
        return render_template('add_user.html')
    else:
        flash("Access denied!")
        return redirect(url_for('home'))


# Route to handle user addition
@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    if not session.get('logged_in'):
        return render_template('login.html')
    elif session.get('admin'):
        if request.method == 'POST':
            nm = request.form['Name']
            ag = request.form['Age']
            pn = request.form['PhoneNumber']
            sl = request.form['SecurityLevel']
            pwd = request.form['Password']

            errors = []
            if not nm.strip():
                errors.append("Name cannot be empty.")
            if not ag.isdigit() or not (0 < int(ag) < 121):
                errors.append("Age must be a whole number between 1 and 120.")
            if not pn.strip():
                errors.append("Phone number cannot be empty.")
            if not sl.isdigit() or not (1 <= int(sl) <= 3):
                errors.append("Security Level must be a number between 1 and 3.")
            if not pwd.strip():
                errors.append("Password cannot be empty.")

            if errors:
                return render_template("result.html", msg=" ".join(errors))

            try:
                with sql.connect('./sql_db/ContestantsDB.db') as con:
                    cur = con.cursor()
                    cur.execute(
                        "INSERT INTO People (Name, Age, PhoneNumber, SecurityLevel, Password) VALUES (?, ?, ?, ?, ?)",
                        (nm, ag, pn, sl, pwd))
                    con.commit()
                    msg = "Record successfully added"
            except Exception as e:
                msg = f"Error in insert operation: {e}"
            finally:
                return render_template("result.html", msg=msg)

    return render_template('add_user.html')

@app.route('/list_all_entries')
def list_all_entries():
    if not check_access(3):
        flash("Access denied!")
        return redirect(url_for('home'))

    try:
        with sql.connect("./sql_db/ContestantsDB.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute('''
                SELECT People.Name, Entry.NameOfBakingItem, Entry.NumExcellentVotes, Entry.NumOkVotes, Entry.NumBadVotes
                FROM Entry
                INNER JOIN People ON Entry.User_ID = People.User_ID;
            ''')
            rows = cur.fetchall()
        return render_template('list_all_entries.html', rows=rows)
    except Exception as e:
        flash(f"Error retrieving contest entries: {e}")
        return redirect(url_for('home'))


# Route to list all users
@app.route('/list_users')
def list_users():
    if not check_access(2):
        flash("Page not found")
        return redirect(url_for('home'))
    elif session.get('admin'):
        try:
            con = sql.connect("./sql_db/ContestantsDB.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM People")
            rows = cur.fetchall()
        except Exception as e:
            flash(f"Error retrieving user list: {e}")
            rows = []
        finally:
            con.close()
        return render_template("list_users.html", rows=rows)
    else:
        flash("Access denied!")
        return redirect(url_for('home'))


# Route to display the form to add a new contest entry
@app.route('/add_contest_entry', methods=['GET', 'POST'])
def add_contest_entry():
    if not check_access(1):
        flash("Page not found")
        return redirect(url_for('home'))
    # Handle form submission and validation

    if request.method == 'POST':
        # Get form data
        item_name = request.form.get('NameOfBakingItem', '').strip()
        excellent_votes = request.form.get('NumExcellentVotes', '0')
        ok_votes = request.form.get('NumOkVotes', '0')
        bad_votes = request.form.get('NumBadVotes', '0')
        user_id = session.get('user_id')  # Assume user_id is stored in the session on login

        # Validate form data
        errors = []
        if not item_name:
            errors.append("The name of the baking item cannot be empty.")
        if not excellent_votes.isdigit() or int(excellent_votes) < 0:
            errors.append("Number of Excellent Votes must be a whole number greater than or equal to 0.")
        if not ok_votes.isdigit() or int(ok_votes) < 0:
            errors.append("Number of OK Votes must be a whole number greater than or equal to 0.")
        if not bad_votes.isdigit() or int(bad_votes) < 0:
            errors.append("Number of Bad Votes must be a whole number greater than or equal to 0.")

        if errors:
            # If validation fails, flash errors and re-display the form
            flash(" ".join(errors))
            return render_template("add_contest_entry.html")

        # If validation passes, insert the new entry into the Entry table
        try:
            with sql.connect('./sql_db/Entry.db') as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO Entry (User_ID, NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes) VALUES (?, ?, ?, ?, ?)",
                    (user_id, item_name, int(excellent_votes), int(ok_votes), int(bad_votes))
                )
                con.commit()
                msg = "Record successfully added"
        except Exception as e:
            msg = f"Error in insert operation: {e}"

        return render_template("result.html", msg=msg)

    # Render the form page for GET requests
    return render_template('add_contest_entry.html')

@app.route('/my_results')
def my_results():
    if not check_access(1):  # Ensure the user has at least Level 1 access
        flash("Access denied!")
        return redirect(url_for('home'))

    user_id = session.get('user_id')  # Retrieve the logged-in user's User_ID
    try:
        # Connect to Entry.db since it holds the contest entries
        with sql.connect("./sql_db/Entry.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()
            # Query to fetch results specific to the user
            cur.execute('''
                SELECT NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes
                FROM Entry
                WHERE User_ID = ?;
            ''', (user_id,))
            rows = cur.fetchall()
        return render_template('my_results.html', rows=rows)  # Pass results to the template
    except Exception as e:
        flash(f"Error retrieving your contest results: {e}")
        return redirect(url_for('home'))
# Route to list contest results
@app.route('/list_results')
def list_results():
    if not check_access(1):
        flash("Page not found")
        return redirect(url_for('home'))
    elif session.get('admin'):
        try:
            con = sql.connect("./sql_db/Entry.db")
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM Entry")
            rows = cur.fetchall()
        except Exception as e:
            flash(f"Error retrieving contest results: {e}")
            rows = []
        finally:
            con.close()
        return render_template("list_results.html", rows=rows)
    else:
        flash("Access denied!")
        return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check admin users in database (Security Level 2 or 3)
        with sql.connect("./sql_db/ContestantsDB.db") as con:
            con.row_factory = sql.Row
            cur = con.cursor()
            cur.execute("SELECT * FROM People WHERE Name = ? AND Password = ?", (username, password))
            user = cur.fetchone()

            if user and user['SecurityLevel'] in (2, 3):
                # Set session details for admin user
                session['logged_in'] = True
                session['username'] = user['Name']
                session['security_level'] = user['SecurityLevel']
                session['admin'] = True
                flash("Welcome, admin user!", "success")
                return redirect(url_for('home'))
            else:
                flash("Invalid username or password for admin!", "danger")
    return render_template('admin_login.html')
# Route to handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            nm = request.form['username']
            pwd = request.form['password']

            with sql.connect("./sql_db/ContestantsDB.db") as con:
                con.row_factory = sql.Row
                cur = con.cursor()
                cur.execute("SELECT * FROM People WHERE Name = ? AND Password = ?", (nm, pwd))
                row = cur.fetchone()

                if row:
                    session['logged_in'] = True
                    session['name'] = row['Name']
                    session['user_id'] = row['User_ID']
                    session['security_level'] = row['SecurityLevel']
                    session['admin'] = (row['SecurityLevel'] >= 2)
                    flash("Logged in successfully!", "success")
                    return redirect(url_for('home'))
                else:
                    session['logged_in'] = False
                    flash("Invalid username and/or password!", "danger")
        except Exception as e:
            flash(f"Login error: {e}", "danger")
    return render_template('login.html')


# Route to handle logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    # Ensure the database directory exists
    if not os.path.exists('./sql_db'):
        os.makedirs('./sql_db')
    # Run the app
    app.secret_key = os.urandom(12)
    app.run(debug=True)
