# web app
import os
from flask import Flask, flash, redirect, url_for, render_template, request, abort, send_file, send_from_directory, session, jsonify
import folium
import json
import requests

# ml
import numpy as np
from PIL import Image
import pandas as pd
from random import randint
import pickle
from sklearn.ensemble import GradientBoostingRegressor

# utils
from util import *
import tempfile

from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

import os.path
from os import path
import socket
import datetime

UPLOAD_FOLDER = '/tempMap'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['SECRET_KEY'] = "supertopsecretprivatekey"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config.update(TEMPLATES_AUTO_RELOAD=True)

app.config['SECRET_KEY'] = "y\xa4\xbf\xb4\xb8\x91\xe8\x9cY\xe7\x80w\xc5\x95\x81\x92\xa8u>\xef\xc1\x01sx"
app.config['PERMANENT_SESSION_LIFETIME'] =  datetime.timedelta(days=5)
#app.config['SECRET_KEY'] = "supertopsecretprivatekey"
#app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#app.config["CACHE_TYPE"] = "null"

def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return {'ip': request.environ['REMOTE_ADDR']}
    else:
        return {'ip': request.environ['HTTP_X_FORWARDED_FOR']}

@app.before_request
def make_session_permanent():
    session.permanent = True
    
# start here
@app.route('/')
def home():
    return redirect(url_for('london'))

@app.route('/seattle', methods=["POST", "GET"])
def seattle():
    session["user_name"] = get_ip()['ip']
    pkl_filename = 'static/model/seattle_model.pkl'
    with open(pkl_filename, 'rb') as file:
        model = pickle.load(file)

    map = folium.Map(location=[47.47, -121.84], tiles="OpenStreetMap", zoom_start=9.4)
    price = -1
    if request.method == "POST":
        lat_form = request.form['lat']
        long_form = request.form['long']
        bed = request.form['inputbed']
        bath = request.form['inputbath']
        sqft_l = request.form['inputsq']
        sqft_lot = request.form['inputsqlot']
        floor = request.form['inputfloor']
        water = request.form["inputwt"]
        view = request.form["inputview"]
        cond = request.form["inputcond"]
        grade = request.form["inputgrade"]
        sqft_a = request.form["inputabove"]
        sqft_b = request.form["inputbase"]
        year = request.form["inputyear"]
        reno = request.form["inputreno"]
        zip = request.form["inputzip"]
        sq_15 = request.form["inputl15"]
        sq_lot15 = request.form["inputlo15"]

        print(lat_form, long_form, bed, bath, sqft_l, sqft_lot, floor, water, view, cond,
              grade, sqft_a, sqft_b, year, reno, zip, sq_15, sq_lot15)

        data={'date': [1],'bedrooms': [bed],'bathrooms':[bath],
        'sqft_living':[sqft_l],'sqft_lot':[sqft_lot],'floors':[floor],
        'waterfront':[water],'view':[view],'condition':[cond],'grade':[grade],
        'sqft_above':[sqft_a],'sqft_basement':[sqft_b],'yr_built':[year],'yr_renovated':[reno],
        'zipcode':[zip],'lat':[lat_form],'long':[long_form],
        'sqft_living15':[sq_15],'sqft_lot15':[sq_lot15]}
        # Create DataFrame
        df = pd.DataFrame(data)
        pred_price_form = model.predict(df).round(1)
        price = pred_price_form[0]
        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Sqft: {sqft_lot}sqft<br>N floors: {floor}<br>N beds: {bed}<br>N bath: {bath}<br>Pred. price: {pred_price_form[0]}$ </i>"
        iframe = folium.IFrame(str, width=200, height=120)
        pop = folium.Popup(iframe, max_width=200)
        folium.Marker([lat_form, long_form], popup=pop, tooltip="Your house",
                      icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(map)


    data = pd.read_csv('static/dataset/kc_house_data.csv')
    conv_dates = [1 if values == 2014 else 0 for values in data.date]
    data['date'] = conv_dates

    with open('us-county.json') as json_file:
        king = json.load(json_file)
    #king = requests.get(url)
    #king = king.json()

    style = {
        "fillOpacity": 0.1,
    }

    with open('london_boroughs.json') as json_file:
        london = json.load(json_file) #url = "https://skgrange.github.io/www/data/london_boroughs.json"
    #london = requests.get(url)
    #london = london.json()

    folium.GeoJson(king, name="King County", style_function=lambda x: style,tooltip=folium.features.GeoJsonTooltip(fields=['namelsad', ], sticky=False, labels=False,localize=True)).add_to(map)
    #folium.GeoJson(king, name="King County", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['JURISDICT_NM',],sticky=False, labels=False, localize=True)).add_to(map)

    poi = pd.read_csv('static/dataset/POI_KingCounty.csv')
    for index, row in poi.iterrows():
        cm = folium.CircleMarker(location=[row.Lat, row.Long], radius=5,tooltip=row.category, fill=True, fill_color='lightblue', color='grey', fill_opacity=0.7)
        map.add_child(cm)
        if index == 50:
            break
    tooltip = "Click for house stats"
    for n in range(15):
        i = randint(0, 20000)
        lat = data.lat[i]
        long = data.long[i]

        bed = data.bedrooms[i]
        bath = data.bathrooms[i]
        sqft = data.sqft_lot[i]
        floors = data.floors[i]
        real_price = data.price[i].round(1)

        x= data.iloc[[i]]
        x = x.drop(['id', 'price'], axis=1)

        pred_price = model.predict(x).round(1)

        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Sqft: {sqft}sqft<br>N floors: {floors}<br>N beds: {bed}<br>N bath: {bath}<br>Price: {real_price}$<br>Pred. price: {pred_price[0]}$ </i>"

        iframe = folium.IFrame(str, width=200, height=120)
        pop = folium.Popup(iframe, max_width=200)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip, icon=folium.Icon(color='cadetblue', icon='home', prefix='fa')).add_to(map)

    map.save("templates/map.html")
    title = "Seatle Housing"
    return render_template("housing.html", pred_form = price, title= title)

@app.route('/user', methods=["GET"])
def get_session():
    return session['user']

@app.route('/currency', methods=["POST"])
def currency():
    if request.method == 'POST':
        session['user']['currency'] = request.form['choice']
        
        apiId = "941abffae69147b7a48685c39f13410d"
        response = requests.get('https://openexchangerates.org/api/latest.json?app_id='+apiId+'&symbols=GBP')
        rate = response.json()['rates']['GBP']
        session['user']['exchangeRate'] = 1/rate
        
        session.modified = True
        print(session['user'])
        return redirect(url_for('london'))
               
@app.route('/london', methods=["POST", "GET"])
def london():
    if not 'user' in session:
        session['user'] = {
            'id' : get_ip()['ip'],
            'recentPoints' : [],
            'currency' : "GBP",
            'SessionCreation' : datetime.datetime.now(),
            'exchangeRate' : None
         }
        session.modified = True
        
    pkl_filename = "static/model/GbFinalLabel_model.pkl"
    with open(pkl_filename, 'rb') as file:
        model = pickle.load(file)

    map = folium.Map(location=[51.509865, -0.118092], tiles="OpenStreetMap", zoom_start=10.5)
    price = -1
    
    style = {
        "fillOpacity": 0.1,
    }

    with open('london_boroughs.json') as json_file:
        london = json.load(json_file) #url = "https://skgrange.github.io/www/data/london_boroughs.json"

    folium.GeoJson(london, name="london", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['name',],sticky=False, labels=False, localize=True)).add_to(map)
    folium.LayerControl().add_to(map)

    #adding 100 random pois to the map
    poi = pd.read_csv("static/dataset/POI_London.csv")
    i = 0
    pos_vector = []
    while(True):
        index = randint(0, 28205)
        if index in pos_vector:
            continue
        pos_vector.append(index)
        row = poi.iloc[index]
        cm = folium.CircleMarker(location=[row.lat, row.long], radius=5,tooltip=row.venue, fill=True, fill_color='lightblue', color='grey', fill_opacity=0.7)
        map.add_child(cm)
        i += 1
        if i == 100:
            break
    
    data = pd.read_csv('static/dataset/LondonFinalLable.csv')
    tooltip = "Click for house stats"
    pos = []
    count = 0
    while(True):
        i = randint(0, 3200)
        if i in pos:
            continue
        pos.append(i)
        lat = data.lat[i]
        long = data.long[i]

        houseType = data.HouseType[i]
        bed = data.NoofBedrooms[i]
        bath = data.NoofBathrooms[i]
        sqft = data.Areainsqft[i]
        distCenter = data.distance_to_london[i]
        real_price = data.Price[i].round(1)
        distHosp = data.DisToHospital[i]
        distSub = data.DisToSubway[i]
        distSchool = data.DisToShool[i]

        x= data.iloc[[i]]
        x = x[['HouseTypeLabel','Areainsqft','NoofBedrooms','NoofBathrooms','NoofReceptions',
                    'distance_to_london','NCrime', 'DisToHospital', 'DisToSubway', 'DisToShool', 'PostalCodeLabel']]

        if session['user']['currency'] == 'USD':
            pred_price = model.predict(x).round(1) * session['user']['exchangeRate']
            real_price = real_price * session['user']['exchangeRate']
            
            str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Type: {houseType}<br>Sqft: {sqft}sqft<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Distance to Hospital: {round(distHosp,1)}km<br>Distance to subway: {round(distSub,1)}km<br>Distance to school: {round(distSchool,1)}km<br>Price: {round(real_price,1)} $<br>Pred. price: {round(pred_price[0],1)}$</i>"
        else:
            pred_price = model.predict(x).round(1)
            str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Type: {houseType}<br>Sqft: {sqft}sqft<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Distance to Hospital: {round(distHosp,1)}km<br>Distance to subway: {round(distSub,1)}km<br>Distance to school: {round(distSchool,1)}km<br>Price: {round(real_price,1)} £<br>Pred. price: {round(pred_price[0],1)}£</i>"

        iframe = folium.IFrame(str, width=260, height=120)
        pop = folium.Popup(iframe, max_width=300)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip, icon=folium.Icon(color='cadetblue', icon='home', prefix='fa')).add_to(map)
        count += 1
        if count == 60:
            break

    if session['user']['recentPoints']:
        for house in session['user']['recentPoints']:
            iframe = folium.IFrame(house['text'], width=260, height=120)
            pop = folium.Popup(iframe, max_width=300)
            folium.Marker(house['loc'], popup=pop, tooltip="Recent Search",
                      icon=folium.Icon(color='purple', icon='home', prefix='fa')).add_to(map)
    
    formData = []
    if request.method == "POST":
        search = request.form['myInput']
        formData.append(search) #0
        
        lat_form = request.form['lat']
        formData.append(lat_form) #1
        
        long_form = request.form['long']
        formData.append(long_form) #2
        
        zip = PostalCodeToLable(request.form['inputzip'])
        formData.append(request.form['inputzip']) #3
        
        bed = int(request.form['inputbed'])
        formData.append(bed) #4
        
        bath = int(request.form['inputbath'])
        formData.append(bath) #5
        
        recep = int(request.form['inputRecep'])
        formData.append(recep) #6
        
        houseType = request.form['inputHouseType']
        houseTypeLabel = HouseTypeToLabel(request.form['inputHouseType'])
        formData.append(houseType) #7
        
        sqft = int(request.form['inputsq'])
        formData.append(sqft) #8
        
        distCenter = distanceToLondon(lat_form, long_form)
        crime = getCrime(request.form['inputzip'])
        distHosp = distanceToHospital(lat_form, long_form)
        distSub = distanceToSubway(lat_form, long_form)
        distSchool = distanceToSchool(lat_form, long_form)
        

        data={'HouseType': houseTypeLabel,'Areainsqft':sqft,'No.ofBedrooms': bed,'No.ofBathrooms': bath,'No.ofReceptions':recep,
                    'distance_to_london':distCenter,'NCrime':crime, 'DisToHospital':distHosp, 'DisToSubway':distSub, 'DisToShool':distSchool, 'PostalCode':zip}
        
        # Create DataFrame
        df = pd.DataFrame(data, index=[0])
        if session['user']['currency'] == 'USD':
            pred_price_form = model.predict(df).round(1) * session['user']['exchangeRate']
            price = round(pred_price_form[0] * session['user']['exchangeRate'],1)
            str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>House type: {houseType}<br>Sqft: {sqft}sqft<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Distance to Hospital: {round(distHosp,1)}km<br>Distance to subway: {round(distSub,1)}km<br>Distance to school: {round(distSchool,1)}km<br>Pred. price: {price}$</i>"
            housePred = {'text' : str, 'loc' : [lat_form, long_form]}
            if not housePred in session['user']['recentPoints']:
                session['user']['recentPoints'].append(housePred)
                session.modified = True
        else:
            pred_price_form = model.predict(df).round(1)
            price = pred_price_form[0]
            str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>House type: {houseType}<br>Sqft: {sqft}sqft<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Distance to Hospital: {round(distHosp,1)}km<br>Distance to subway: {round(distSub,1)}km<br>Distance to school: {round(distSchool,1)}km<br>Pred. price: {price}£</i>"
            housePred = {'text' : str, 'loc' : [lat_form, long_form]}
            if not housePred in session['user']['recentPoints']:
                session['user']['recentPoints'].append(housePred)
                session.modified = True
            
        iframe = folium.IFrame(str, width=260, height=120)
        pop = folium.Popup(iframe, max_width=300)
        folium.Marker([lat_form, long_form], popup=pop, tooltip="Your house",
                      icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(map)
    
        

    map.save("templates/map.html")
    
    title = "London Housing"
    postalcode = pd.read_csv('static/dataset/PostcodeLabel.csv')
    post = postalcode['Postcode'].tolist()
    
    return render_template("housing.html", pred_form = price, title= title, postal = post, currency= session['user']['currency'], formData = formData)

@app.route('/deletePoints', methods = ['POST'])
def deletePoints():
    session['user']['recentPoints'] = []
    return redirect(url_for('london'))

@app.route('/map')
def map():
    return render_template('map.html')

@app.errorhandler(404)
def error404(e):
    return render_template("error.html"), 404

@app.errorhandler(403)
def error403(e):
    return render_template("erro.html"), 403

@app.errorhandler(500)
def error500(e):
    return render_template("error.html"), 500

@app.errorhandler(405)
def error405(e):
    return render_template("error.html"), 405

if __name__ == '__main__':
    app.run()
