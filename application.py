from flask.helpers import url_for
import mysql.connector
import os
from flask import Flask, make_response, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, month_number_conversion
from report import PDF
import smtplib
from email.message import EmailMessage


app=Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
# configure sessions
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# establish connector with MySQL server with environemntal log-in
db = mysql.connector.connect(
    host='localhost',
    user=os.environ.get('DB_USER'),
    passwd=os.environ.get('DB_PASS'),
)
# using documentation as the database and establish connection between mycursor and db
mycursor = db.cursor()
mycursor.execute("USE documentation")


def generate_report(ClientID, Month, Year, Client_Name):
    # select all goals of that client in history
    mycursor.execute('SELECT id, Goal1, Goal2, Goal3 FROM Notes WHERE type = "goals" AND ClientInfo_id = %s ORDER BY id DESC', (ClientID,))
    goals = mycursor.fetchall()
    # select the ids of all records including goals/objectives and their outcomes
    mycursor.execute("SELECT MIN(id) FROM Notes WHERE type = 'document' AND DocMonth = %s AND DocYear = %s AND ClientInfo_id = %s", (Month, Year, ClientID))
    first_record_id = mycursor.fetchall()[0][0]
    for content in goals:
        if content[0] < first_record_id:
            Goal1 = content[1]
            Goal2 = content[2]
            Goal3 = content[3]
            note_id = content[0]
            break
        else:
            continue

    # initialize three tables of data
    Goal1_Data = [
        ["Objectives"],[],[],[],
    ]
    Goal2_Data = [
        ["Objectives"],[],[],[],
    ]
    Goal3_Data = [
        ["Objectives"],[],[],[],
    ]
    # access the dates for the search criteria
    mycursor.execute('SELECT DocDate FROM Notes WHERE DocMonth = %s AND DocYear = %s AND ClientInfo_id = %s', (Month,Year,ClientID))
    Date = mycursor.fetchall()
    for i in Date:
        Goal1_Data[0].append(str(Month) + "/"+ str(i[0]))
        Goal2_Data[0].append(str(Month) + "/"+ str(i[0]))
        Goal3_Data[0].append(str(Month) + "/"+ str(i[0]))
    # access objectives and objective outcomes for all three goals
    #goal1
    mycursor.execute('SELECT Ob1, Ob2, Ob3 FROM Notes WHERE type = "goals" AND ClientInfo_id = %s AND id = %s', (ClientID,note_id))
    ob123 = mycursor.fetchall()
    mycursor.execute('SELECT Ob1_outcome, Ob2_outcome, Ob3_outcome FROM Notes WHERE type = "document" AND ClientInfo_id = %s AND DocMonth = %s AND DocYear = %s', (ClientID,Month,Year))
    ob123_outcome = mycursor.fetchall()
    for i in range(1,4):
        ob123[0] = list(ob123[0])
        if ob123[0][i-1] is None:
            ob123[0][i-1] = ''
        Goal1_Data[i].append(str(ob123[0][i-1]))
    for i in  ob123_outcome:
        i = list(i)
        for j in range(3):
            if i[j] is None:
                i[j] = ''
            Goal1_Data[j+1].append(str(i[j]))
    #goal2
    mycursor.execute('SELECT Ob4, Ob5, Ob6 FROM Notes WHERE type = "goals" AND ClientInfo_id = %s AND id = %s', (ClientID, note_id))
    ob456 = mycursor.fetchall()
    mycursor.execute('SELECT Ob4_outcome, Ob5_outcome, Ob6_outcome FROM Notes WHERE type = "document" AND ClientInfo_id = %s AND DocMonth = %s AND DocYear = %s', (ClientID,Month,Year))
    ob456_outcome = mycursor.fetchall()
    for i in range(1,4):
        ob456[0]= list(ob456[0])
        if ob456[0][i-1] is None:
            ob456[0][i-1] = ''
        Goal2_Data[i].append(str(ob456[0][i-1]))
    for i in  ob456_outcome:
        i = list(i)
        for j in range(3):
            if i[j] is None:
                i[j] = ''
            Goal2_Data[j+1].append(str(i[j]))
    #goal3
    mycursor.execute('SELECT Ob7, Ob8, Ob9 FROM Notes WHERE type = "goals" AND ClientInfo_id = %s AND id = %s', (ClientID, note_id))
    ob789 = mycursor.fetchall()
    mycursor.execute('SELECT Ob7_outcome, Ob8_outcome, Ob9_outcome FROM Notes WHERE type = "document" AND ClientInfo_id = %s AND DocMonth = %s AND DocYear = %s', (ClientID,Month,Year))
    ob789_outcome = mycursor.fetchall()
    for i in range(1,4):
        ob789[0] = list(ob789[0])
        if ob789[0][i-1] is None:
            ob789[0][i-1] = ''
        Goal3_Data[i].append(str(ob789[0][i-1]))
    for i in  ob789_outcome:
        i = list(i)
        for j in range(3):
            if i[j] is None:
                i[j] = ''
            Goal3_Data[j+1].append(str(i[j]))
    pdf = PDF('L', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
    pdf.set_font('DejaVu', '', 16)
    # create PDF headers
    pdf.cell(0, 10, 'Music Therapy Report', align='C', ln=True)
    pdf.cell(0, 10, f'Client Name: {Client_Name}', ln=True)
    pdf.cell(0, 10, f'Date: {Month}/{Year}', ln=True)
    # create goal and objective tables
    if Goal1 not in ['', None]:
        pdf.create_table(table_data = Goal1_Data, title=f'Goal 1: {Goal1}', cell_width=[120,20,20,20,20,20])
        pdf.ln()
    if Goal2 not in ['', None]:
        pdf.create_table(table_data = Goal2_Data, title=f'Goal 2: {Goal2}', cell_width=[120,20,20,20,20,20])
        pdf.ln()
    if Goal3 not in ['', None]:
        pdf.create_table(table_data = Goal3_Data, title=f'Goal 3: {Goal3}', cell_width=[120,20,20,20,20,20])
        pdf.ln()
    # create narrative notes
    mycursor.execute('SELECT Narrative_note FROM Notes WHERE type = "document" AND ClientInfo_id = %s AND DocMonth = %s AND DocYear = %s', (ClientID,Month,Year))
    narrative_notes = mycursor.fetchall()
    j = 1
    for i in narrative_notes:
        i = list(i)
        # extracting the table date value to put in front of the notes
        if j <= len(Goal1_Data[0]) - 1:
            i[0] = Goal1_Data[0][j] + ' ' + i[0]
            pdf.multi_cell(0, 5, i[0])
            pdf.ln()
            j = j + 1
    return pdf.output(dest='S')

@app.route("/email", methods=["GET", "POST"])
@login_required
def email():
    if request.method == 'GET':
        return render_template('email.html')
    else:
        email_address = os.environ.get('GG_USER')
        email_password = os.environ.get('GG_PASS')
        Month = int(request.form.get('Month'))
        Year = int(request.form.get('Year'))
        Month_text = month_number_conversion(Month)
        user_id = session['user_id']
        mycursor.execute("SELECT Caregiver_Email, Client_Name, ClientInfo_id FROM ClientInfo INNER JOIN Therapist ON Therapist.idTherapist = ClientInfo.Therapist_idTherapist INNER JOIN Notes ON Notes.ClientInfo_id = ClientInfo.id WHERE Therapist.username=%s AND DocYear=%s AND DocMonth=%s GROUP BY Client_Name, Caregiver_Email, ClientInfo_id",(user_id, Year, Month))
        #pull all the caregiver emails and client names out based on the therapist and the eligible clients who got documented that month/year
        contacts = mycursor.fetchall()
        #if the client doesn't have caregiver_email, skip this client
        contacts = [i for i in contacts if i[0] !='' or None]
        for contact in contacts:
            receiver = contact[0]
            Client_Name = contact[1]
            ClientID = contact[2]
            result_file = generate_report(ClientID, Month, Year, Client_Name)
            file_name = f"{Client_Name} {Month} {Year}.pdf"
            msg = EmailMessage()
            msg['Subject'] = f'{Month_text} Report'
            msg['From'] = email_address
            msg['To'] = receiver
            msg.set_content(f'Greetings, \n\nAttached is my progress note with {Client_Name.split()[0]} in {Month_text}. If you have any questions, please let me know. \n\nThank you! \n\nNote: Please do not reply directly to this email. Instead send all communication/inquiries to hu.yuffie@macphail.org')
            msg.add_attachment(result_file, maintype='application', subtype='pdf', filename=file_name)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(email_address, email_password)
                smtp.send_message(msg)
        return redirect('/')

@app.route("/reports", methods=["GET", "POST"])
@login_required
def generate():
    if request.method == 'GET':
        return render_template('reports.html')
    else:
        # get info from HTML and login user
        Month = request.form.get('Month')
        Year = request.form.get('Year')
        Client_Name = request.form.get('ClientName')
        # access logged in therapist's Client
        user_id = session['user_id']
        mycursor.execute("SELECT idTherapist FROM Therapist WHERE username = %s", (user_id,))
        userid = mycursor.fetchall()[0][0]
        userid = int(userid)
        mycursor.execute("SELECT id FROM ClientInfo WHERE Client_Name = %s AND Therapist_idTherapist = %s", (Client_Name, userid))
        ClientID = mycursor.fetchall()[0][0]
        # access goals for this client
        result = generate_report(ClientID, Month, Year, Client_Name)
        response = make_response(result)
        response.headers.set('Content-Disposition', 'attachment', filename=Client_Name + Month + Year + '.pdf')
        response.headers.set('Content-Type', 'application/pdf')
        return response


# homepage after logging in
@app.route("/")
@login_required
def welcome():
    user_id = session['user_id']
    return render_template("welcome.html", user=user_id)

@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    user_id = session['user_id']
    if request.method == "GET":
        return render_template("update.html")
    else:
        Client_Name = request.form.get('Client_Name')
        try:
            mycursor.execute("SELECT idTherapist FROM Therapist WHERE username = %s", (user_id,))
            userid = mycursor.fetchall()[0][0]
            mycursor.execute("SELECT id FROM ClientInfo WHERE Client_Name = %s AND Therapist_idTherapist = %s", (Client_Name, userid))
            ClientID = mycursor.fetchall()[0][0]
        except:
            return apology("Invalid client name or client doesn't exist. Please try again.")
        return redirect(url_for("update_records", ClientID=ClientID))

@app.route("/update/<ClientID>", methods=["GET", "POST"])
@login_required
def update_records(ClientID):
    if request.method == "GET":
        mycursor.execute('SELECT Goal1, Ob1, Ob2, Ob3, Goal2, Ob4, Ob5, Ob6, Goal3, Ob7, Ob8, Ob9, ClientInfo_id FROM Notes WHERE id IN (SELECT MAX(id) FROM Notes WHERE type = "goals" AND ClientInfo_id = %s)', (ClientID,))
        allgoals = mycursor.fetchall()[0]
        allgoalsID = ['Goal 1 ORI', 'Objective 1 ORI', 'Objective 2 ORI', 'Objective 3 ORI', 'Goal 2 ORI', 'Objective 4 ORI', 'Objective 5 ORI', 'Objective 6 ORI', 'Goal 3 ORI', 'Objective 7 ORI', 'Objective 8 ORI', 'Objective 9 ORI', 'Info ORI']
        titles = ['Goal 1', 'Objective 1', 'Objective 2', 'Objective 3', 'Goal 2', 'Objective 1', 'Objective 2', 'Objective 3', 'Goal 3', 'Objective 1', 'Objective 2', 'Objective 3']
        htmlLabels = ['Goal 1', 'Objective 1', 'Objective 2', 'Objective 3', 'Goal 2', 'Objective 4', 'Objective 5', 'Objective 6', 'Goal 3', 'Objective 7', 'Objective 8', 'Objective 9', 'Info']
        inputIds = ['Goal 1 input', 'Objective 1 input', 'Objective 2 input', 'Objective 3 input', 'Goal 2 input', 'Objective 4 input', 'Objective 5 input', 'Objective 6 input', 'Goal 3 input', 'Objective 7 input', 'Objective 8 input', 'Objective 9 input', 'Info input']
        return render_template('update_records.html', allgoals = allgoals, titles=titles, htmlLabels = htmlLabels, inputIds = inputIds, allgoalsID = allgoalsID)
    else:
        update_list = request.form.getlist('update')
        print("yo look at me", len(update_list))
        # error checking making sure there is date input
        if '' in update_list[:3]:
            return apology("Must provide today's date")
        for i in range(len(update_list)):
            if update_list[i] == 'None' or '':
                update_list[i] = None
        update_list[-1] = int(update_list[-1])
        update_list.append('goals')
        update_list=tuple(update_list)
        mycursor.execute("INSERT INTO Notes (DocDate, DocMonth, DocYear, Goal1, Ob1, Ob2, Ob3, Goal2, Ob4, Ob5, Ob6, Goal3, Ob7, Ob8, Ob9, ClientInfo_id, type) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", update_list)
        db.commit()
        return redirect('/')

@app.route("/existing_client", methods=["GET", "POST"])
@login_required
def existingclient():
    user_id = session['user_id']
    if request.method == "GET":
        return render_template("existing_client.html")
    else:
        Client_Name = request.form.get('Client_Name')
        try:
            mycursor.execute("SELECT idTherapist FROM Therapist WHERE username = %s", (user_id,))
            userid = mycursor.fetchall()[0][0]
            mycursor.execute("SELECT id FROM ClientInfo WHERE Client_Name = %s AND Therapist_idTherapist = %s", (Client_Name, userid))
            ClientID = mycursor.fetchall()[0][0]
        except:
            return apology("Invalid client name or client doesn't exist. Please try again.")
        return redirect(url_for("document", ClientID=ClientID))

@app.route("/existing_clinet/<ClientID>", methods=["GET", "POST"])
@login_required
def document(ClientID):
    display1 = []
    if request.method == "GET":
        mycursor.execute('SELECT Goal1, Ob1, Ob2, Ob3, Goal2, Ob4, Ob5, Ob6, Goal3, Ob7, Ob8, Ob9, ClientInfo_id FROM Notes WHERE id IN (SELECT MAX(id) FROM Notes WHERE type = "goals" AND ClientInfo_id = %s)', (ClientID,))
        allgoals = mycursor.fetchall()[0]
        for i in allgoals:
            if i is None:
                i = ''
            display1.append(i)
        display1 = tuple(display1)
        return render_template('document.html', block1 = display1)
    else:
        # get all data to input into SQL server in order including clientid, docdates, Yes/No/NA, and narrative note
        outcome_list = request.form.getlist('outcome')
        # make sure those that aren't filled due to absence of objectives and those that are goals and thus have no outcomes, be injected in SQL with Null value
        for i in range(len(outcome_list)):
            if outcome_list[i] == 'NULL':
                outcome_list[i] = None
        # the clientid is passed initially as string so we need to convert to INT to fit SQL datatype
        outcome_list[-1] = int(outcome_list[-1])
        outcome_list.append('document')
        # convert the list to tuple to inject into the database
        outcome_list = tuple(outcome_list)
        mycursor.execute('INSERT INTO Notes (DocDate, DocMonth, DocYear, Narrative_note, Goal1, Ob1_outcome, Ob2_outcome, Ob3_outcome, Goal2, Ob4_outcome, Ob5_outcome, Ob6_outcome, Goal3, Ob7_outcome, Ob8_outcome, Ob9_outcome, ClientInfo_id, type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', outcome_list)
        db.commit()
        return redirect('/')
# new client input information
@app.route("/new_client", methods=["GET", "POST"])
@login_required
def newclient():
    user_id = session['user_id']
    if request.method == "GET":
        return render_template("new_client.html")
    else:
        # error checking. client name has to be provided.
        if not request.form.get("Client_Name"):
            return apology("Must provide client name.")
        new_list = request.form.getlist('new')
        #error checking there is date input
        if '' in new_list[-3:]:
            return apology("Must provide today's date")
        for i in range(len(new_list)):
            if new_list[i] == '':
                new_list[i] = None
        # extract foreign key for the next INSERT query
        mycursor.execute("SELECT idTherapist FROM Therapist WHERE username = %s", (user_id,))
        therapist_id = mycursor.fetchall()[0][0]
        therapist_id = int(therapist_id)
        Client_Name = request.form.get('Client_Name')
        mycursor.execute("INSERT INTO ClientInfo (Client_Name, Caregiver_Email, Birthday, Therapist_idTherapist) VALUES(%s,%s,%s,%s)",
                        (Client_Name, new_list[0], new_list[1], therapist_id))
        db.commit()
        new_list.append('goals')
        mycursor.execute("SELECT id FROM ClientInfo WHERE Client_Name = %s", (Client_Name,))
        ClientID = mycursor.fetchall()[0][0]
        ClientID = int(ClientID)
        new_list.append(ClientID)
        new_list = tuple(new_list)
        mycursor.execute("INSERT INTO Notes (Goal1, Ob1, Ob2, Ob3, Goal2, Ob4, Ob5, Ob6, Goal3, Ob7, Ob8, Ob9, DocDate, DocMonth, DocYear, type, ClientInfo_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        new_list[2:])
        db.commit()
        return redirect('/')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        mycursor.execute("SELECT * FROM Therapist WHERE username = %s", (request.form.get("username"),))
        rows = mycursor.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0][1]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        if not request.form.get('username'):
            return apology("Please provide username.")
        elif not request.form.get('password'):
            return apology("Please provide password.")
        elif not request.form.get('confirmation'):
            return apology("Please re-type your password")
        elif request.form.get('password') != request.form.get('confirmation'):
            return apology("Please make sure your passwords match.")
        Username = request.form.get('username')
        Password = request.form.get('password')
        Hash = generate_password_hash(Password)
        try:
            mycursor.execute("INSERT INTO Therapist (username, hash) VALUES (%s, %s)", (Username, Hash))
            db.commit()
        except:
            return apology('Username has already been registered.')
        return redirect("/")
