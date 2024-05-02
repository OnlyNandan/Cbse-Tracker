from flask import Flask, render_template, request, redirect, url_for, flash
from bs4 import BeautifulSoup
import requests
import time
import threading
import mysql.connector
from mysql.connector import Error
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = "S@^a6"
datefound, trigger1, trigger2,pre,valid = False, False, False, False , False

sender_email = "botter0912@gmail.com"
sender_password = "h"

def create_connection():
    hostname = "localhost"
    username = "user"
    password = "password"
    database = "cbse"
    try:
        connection = mysql.connector.connect(
            host=hostname, username=username, password=password, database=database)
        return connection
    except Error as e:
        print(e)

def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS Mail (id INT AUTO_INCREMENT PRIMARY KEY, email VARCHAR(255), mailsent1 BOOLEAN DEFAULT FALSE, mailsent2 BOOLEAN DEFAULT FALSE, mailsentboth BOOLEAN DEFAULT FALSE)")
    connection.commit()

def send_email(sender_email, sender_password, recipient_email, subject, body):
    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = subject

    # Attach the body to the MIME message
    message.attach(MIMEText(body, "plain"))

    # Create SMTP session for sending the mail
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Enable TLS
        server.login(sender_email, sender_password)  # Login to Gmail
        text = message.as_string()
        server.sendmail(sender_email, recipient_email, text)  # Send the email



def scrape_data():
    while True:
        scrape = requests.get('http://web.archive.org/web/20240319104152/https://results.cbse.nic.in/')
        scrape2 = requests.get('https://cbseresults.nic.in/2024')
        soup = BeautifulSoup(scrape.text, 'html.parser')
        soup2 = BeautifulSoup(scrape2.text, 'html.parser')
        last_updated_date = "Mar 21, 2024"

        bigsample = soup.find_all('strong',class_ = '')
        cbseresults = soup2.find_all('body',class_ = "")


        if cbseresults[0].text.strip() == "Some error occurred, please try again after sometime.":
            trigger1 = False
        else:
            trigger1 = True

        for data in bigsample:
            if data.text.endswith("2024"):
                datefound = True
                if data.text == last_updated_date:
                    trigger2 = False
                else:
                    trigger2 = True
            else:
                pass

        if datefound == False:
            trigger2 = False
            print("(Year-Error): - The year is not 2024")


        if trigger1 == True and trigger2 == True:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Mail")
            result = cursor.fetchall()
            for i in result:
                if i[4] == False:
                    send_email(sender_email, sender_password, i[1], "CBSE Results 2024", "The results have been declared, Both Triggers are Triggered. ALL THE BEST SOLDIER")
                    cursor.execute("UPDATE Mail SET mailsentboth = TRUE WHERE email = %s", (i[1],))
                    connection.commit()
        elif trigger1 == True and trigger2 == False:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Mail")
            result = cursor.fetchall()
            for i in result:
                if i[2] == False:
                    send_email(sender_email, sender_password, i[1], "CBSE Results 2024", "The results have been declared, Trigger 1 is Triggered(results page). ALL THE BEST SOLDIER")
                    cursor.execute("UPDATE Mail SET mailsent1 = TRUE WHERE email = %s", (i[1],))
                    connection.commit()
        elif trigger1 == False and trigger2 == True:
            connection = create_connection()
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM Mail")
            result = cursor.fetchall()
            for i in result:
                if i[3] == False:
                    send_email(sender_email, sender_password, i[1], "CBSE Results 2024", "Website has been updated, Trigger 2 is Triggered(date). ALL THE BEST SOLDIER")
                    cursor.execute("UPDATE Mail SET mailsent2 = TRUE WHERE email = %s", (i[1],))
                    connection.commit()
        time.sleep(120)  # Pause execution for 2 minutes


def datas2():
    scrape = requests.get('https://results.cbse.nic.in/')
    scrape2 = requests.get('https://cbseresults.nic.in/2024')
    soup = BeautifulSoup(scrape.text, 'html.parser')
    soup2 = BeautifulSoup(scrape2.text, 'html.parser')
    datefound, trigger1, trigger2 = False, False, False
    last_updated_date = "Mar 21, 2024"

    bigsample = soup.find_all('strong',class_ = '')
    cbseresults = soup2.find_all('body',class_ = "")

    
    if cbseresults[0].text.strip() == "Some error occurred, please try again after sometime.":
        t1 = False
    else:
        t1 = True


    for data in bigsample:
        if data.text.endswith("2024"):
            datefound = True
            if data.text == last_updated_date:
                t2 = False
            else:
                t2 = True
        else:
            pass

    if datefound == False:
        t2 = False
        print("(Year-Error): - The year is not 2024")

    return t1, t2
@app.route('/', methods=['GET', 'POST'])
def home():
    t1,t2 = datas2()
    if request.method == 'POST':
        email = request.form['email']
        if email.endswith("@gmail.com") or email.endswith("@yahoo.com") or email.endswith("@hotmail.com") or email.endswith("@outlook.com"):
            valid = True
        print("Email:", email)
        connection = create_connection()
        if connection and valid == True:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM Mail WHERE email = %s", (email,))
                result = cursor.fetchall()
                for i in result:
                    if i[1].lower() == email.lower():
                        flash("Email already exists")
                        pre = True
                        return redirect(url_for('home'))
                    else:
                        pre = False
                if not pre:
                    cursor.execute("INSERT INTO Mail (email) VALUES (%s)", (email,))
                    connection.commit()
                    cursor.close()
                    connection.close()
                else:
                    pass
            except mysql.connector.Error as e:
                print("Error inserting data into database:", e)
                flash("Error inserting email into database")
        return redirect(url_for('home'))
    return render_template('index.html', trigger1=t1, trigger2=t2)

if __name__ == "__main__":
    t = threading.Thread(target=scrape_data)
    t.start()
    create_table(create_connection())
    app.run(debug=True, port=1111)
