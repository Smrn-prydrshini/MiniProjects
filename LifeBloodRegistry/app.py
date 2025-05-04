from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
import config

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = config.Config.MYSQL_HOST
app.config['MYSQL_USER'] = config.Config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.Config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.Config.MYSQL_DB

mysql = MySQL(app)

# Routes for the blood donation system

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Add donor
@app.route('/add_donor', methods=['GET', 'POST'])
def add_donor():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        blood_type = request.form['blood_type']
        contact_no = request.form['contact_no']
        last_donation = request.form['last_donation']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO Donors (name, age, blood_type, contact_no, last_donation) VALUES (%s, %s, %s, %s, %s)", 
                       (name, age, blood_type, contact_no, last_donation))
        mysql.connection.commit()
        return redirect(url_for('view_donors'))
    
    return render_template('add_donor.html')

# View all donors
@app.route('/view_donors')
def view_donors():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Donors")
    donors = cursor.fetchall()
    return render_template('view_donors.html', donors=donors)

# Add blood bank
@app.route('/add_blood_bank', methods=['GET', 'POST'])
def add_blood_bank():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        contact_no = request.form['contact_no']
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO BloodBanks (name, location, contact_no) VALUES (%s, %s, %s)", 
                       (name, location, contact_no))
        mysql.connection.commit()
        return redirect(url_for('view_blood_banks'))
    
    return render_template('add_blood_bank.html')

# View all blood banks
@app.route('/view_blood_banks')
def view_blood_banks():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM BloodBanks")
    blood_banks = cursor.fetchall()
    return render_template('view_blood_banks.html', blood_banks=blood_banks)

# Add blood request
@app.route('/add_blood_request', methods=['GET', 'POST'])
def add_blood_request():
    if request.method == 'POST':
        recipient_name = request.form['recipient_name']
        blood_type = request.form['blood_type']
        quantity = request.form['quantity']
        request_status = 'Pending'
        
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO BloodRequests (recipient_name, blood_type, quantity, request_status) VALUES (%s, %s, %s, %s)", 
                       (recipient_name, blood_type, quantity, request_status))
        mysql.connection.commit()
        return redirect(url_for('view_blood_requests'))
    
    return render_template('add_blood_request.html')

# View all blood requests
@app.route('/view_blood_requests')
def view_blood_requests():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM BloodRequests")
    blood_requests = cursor.fetchall()
    return render_template('view_blood_requests.html', blood_requests=blood_requests)

# View blood inventory
@app.route('/view_inventory')
def view_inventory():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM BloodInventory")
    inventory = cursor.fetchall()
    return render_template('view_inventory.html', inventory=inventory)

# View blood units
@app.route('/view_blood_units')
def view_blood_units():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM BloodUnits")
    blood_units = cursor.fetchall()
    return render_template('view_blood_units.html', blood_units=blood_units)

if __name__ == "__main__":
    app.run(debug=True)
