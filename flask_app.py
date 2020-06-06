# doing necessary imports

from flask import Flask, render_template, request,jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import Request,urlopen as uReq
import json
import pandas as pd
from pymongo import MongoClient

app = Flask(__name__)  # initialising the flask app with the name 'app'




@app.route('/',methods=['POST','GET']) # route with allowed methods as POST and GET
def index():
    if request.method == 'POST':
        searchString = request.form['content'].replace(" ","") # obtaining the search string entered in the form
        try:
            client = MongoClient()
            client = MongoClient("localhost", 27017)
            client = MongoClient('mongodb://127.0.0.1:27017/')
            db = client['COVIDDB']
            my_db_query = {'searchString': searchString}  # connecting to the database called crawlerDB
            review = db.Cntry_Covid.find_one(my_db_query)
            reviews = []
            reviews.append(review)
            # searching the collection with the name same as the keyword
            if review != None:  # if there is a collection with searched keyword and it has records in it
                return render_template('results.html', reviews=reviews)  # show the results to user
            else:
                covid_url = r"https://www.worldometers.info/coronavirus/country/" + searchString + "/"
                req = Request(covid_url, headers={'User-Agent': 'Mozilla/5.0'})
                uclient = uReq(req)
                page = uclient.read()
                page_soup = bs(page, "html.parser")
                data = page_soup.find_all('div', {'class': 'maincounter-number'})
                headers = page_soup.find_all('div', {'id': 'maincounter-wrap'})
                country = page_soup.find_all('div', {'class': 'label-counter'})
                t = []
                for tag in country:
                    t.append(tag.text.split("/")[2].strip())

                # heading = headers.find_all('h1')
                key = []
                for h in headers:
                    if h.h1 != None:
                        k = h.h1.text
                        key.append(k)
                key_mod = []
                key_mod.append("Country")

                for l in key:
                    li = l.replace(":", "")
                    key_mod.append(li)

                val = []
                val.extend(t)
                for dat in data:
                    v = dat.span.text
                    val.append(v)
                key_mod.append("searchString")
                val.append(searchString)
                Country_Covid = dict(zip(key_mod, val))
                data = db.Cntry_Covid
                result = db.Cntry_Covid.insert_one(Country_Covid)
                reviews = []
                reviews.append(Country_Covid)
                # searching the collection with the name same as the keyword
                if len(Country_Covid) > 0:  # if there is a collection with searched keyword and it has records in it
                    return render_template('results.html', reviews=reviews)
                # show the results to user
        except:
            return 'Data Not Found'
    else:
        return render_template('index.html')
if __name__ == "__main__":
    app.run(port=8000,debug=True) # running the app on the local machine on port 8000