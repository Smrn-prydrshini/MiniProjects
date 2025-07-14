from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'LifeBloodRegistry'

mysql = MySQL(app)

# ---------------- HOME PAGE ----------------
@app.route('/')
def index():
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM DonorDetails")
    total_donors = cursor.fetchone()[0]

    cursor.execute("SELECT IFNULL(SUM(Quantity), 0) FROM BloodUnits")
    total_units_donated = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM BloodRequests WHERE Status = 'Fulfilled'")
    total_requests_fulfilled = cursor.fetchone()[0]

    cursor.close()
    return render_template('index.html',
                           total_donors=total_donors,
                           total_units_donated=total_units_donated,
                           total_requests_fulfilled=total_requests_fulfilled)

# ---------------- VIEW BLOOD BANKS ----------------
@app.route('/view_blood_banks')
def view_blood_banks():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM BloodBanks")
    blood_banks = cursor.fetchall()
    cursor.close()
    return render_template('view_blood_banks.html', blood_banks=blood_banks)

# ---------------- VIEW DONORS ----------------
@app.route('/view_donors')
def view_donors():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM DonorDetails")
    donors = cursor.fetchall()
    cursor.close()
    return render_template('view_donors.html', donors=donors)

# ---------------- ADD DONOR ----------------
@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        Name = request.form['Name']
        Age = request.form['Age']
        Gender = request.form['Gender']
        BloodType = request.form['BloodType']
        ContactNo = request.form['ContactNo']
        Address = request.form['Address']
        LastDonationDate = request.form['LastDonationDate'] or None

        cursor = mysql.connection.cursor()
        cursor.callproc('AddDonor', (Name, Age, Gender, BloodType, ContactNo, Address, LastDonationDate))
        mysql.connection.commit()
        cursor.close()

        flash("Donor added successfully!")
        return redirect(url_for('add_donor'))

    return render_template('add_donor.html')

# ---------------- VIEW DONATION SUMMARY ----------------
@app.route('/donation_summary')
def donation_summary():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM DonationSummary")
    summary = cursor.fetchall()
    cursor.close()
    return render_template('donation_summary.html', summary=summary)

# ---------------- REQUEST BLOOD ----------------
@app.route('/request_blood', methods=['GET', 'POST'])
def request_blood():
    if request.method == 'POST':
        Name = request.form['Name']
        Age = request.form['Age']
        Gender = request.form['Gender']
        BloodType = request.form['BloodType']
        ContactNo = request.form['ContactNo']
        Address = request.form['Address']
        RequestDate = datetime.today().strftime('%Y-%m-%d')
        Quantity = int(request.form['Quantity'])

        cursor = mysql.connection.cursor()

        cursor.execute("""INSERT INTO RecipientDetails 
                          (Name, Age, Gender, BloodType, ContactNo, Address, RequestDate) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                          (Name, Age, Gender, BloodType, ContactNo, Address, RequestDate))
        RecipientID = cursor.lastrowid

        cursor.execute("""INSERT INTO BloodRequests 
                          (RecipientID, BloodType, Quantity, RequestDate, Status) 
                          VALUES (%s, %s, %s, %s, 'Pending')""",
                          (RecipientID, BloodType, Quantity, RequestDate))

        mysql.connection.commit()
        cursor.close()

        flash("Blood request submitted successfully!")
        return redirect(url_for('request_blood'))

    return render_template('request_blood.html')

# ---------------- FULFILL BLOOD REQUEST ----------------
@app.route('/fulfill_request/<int:RequestID>')
def fulfill_request(RequestID):
    cursor = mysql.connection.cursor()
    cursor.callproc('FulfillBloodRequest', (RequestID,))
    mysql.connection.commit()
    cursor.close()

    flash(f"Request ID {RequestID} fulfilled successfully!")
    return redirect(url_for('index'))

# ---------------- RUN FLASK ----------------
if __name__ == '__main__':
    app.run(debug=True)
