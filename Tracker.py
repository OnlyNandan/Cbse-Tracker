from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)
app.secret_key = "S@^a6"

scrape = requests.get('https://results.cbse.nic.in/')
scrape2 = requests.get('https://cbseresults.nic.in/2024')
soup = BeautifulSoup(scrape.text, 'html.parser')
soup2 = BeautifulSoup(scrape2.text, 'html.parser')
datefound, trigger1, trigger2 = False, False, False
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

print(trigger2)
print(trigger1)


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', trigger1=trigger1, trigger2=trigger2)

if __name__ == "__main__":
    app.run(debug=True, port=1281)


