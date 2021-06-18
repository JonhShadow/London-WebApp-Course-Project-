# web app
import os
from flask import Flask, flash, redirect, url_for, render_template, request
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

app = Flask(__name__)
app.config['SECRET_KEY'] = "supertopsecretprivatekey"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config["CACHE_TYPE"] = "null"
app.config.update( DEBUG=True, TEMPLATES_AUTO_RELOAD=True)

# start here
@app.route('/')
def home():
    return redirect(url_for('london'))

@app.route('/seattle', methods=["POST", "GET"])
def seattle():
    pkl_filename = "house_model.pkl"
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
        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Sqft: {sqft_lot}sq<br>N floors: {floor}<br>N beds: {bed}<br>N bath: {bath}<br>Pred. price: {pred_price_form[0]}$ </i>"
        iframe = folium.IFrame(str, width=200, height=120)
        pop = folium.Popup(iframe, max_width=200)
        folium.Marker([lat_form, long_form], popup=pop, tooltip="Your house",
                      icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(map)


    data = pd.read_csv("kc_house_data.csv")
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

    folium.GeoJson(london, name="london", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['name',],sticky=False, labels=False, localize=True)).add_to(map)
    folium.LayerControl().add_to(map)

    poi = pd.read_csv("POI_KingCounty.csv")
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

        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Sqft: {sqft}sq<br>N floors: {floors}<br>N beds: {bed}<br>N bath: {bath}<br>Price: {real_price}$<br>Pred. price: {pred_price[0]}$ </i>"

        iframe = folium.IFrame(str, width=200, height=120)
        pop = folium.Popup(iframe, max_width=200)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip, icon=folium.Icon(color='cadetblue', icon='home', prefix='fa')).add_to(map)

    map.save("templates/map.html")
    title = "Seatle Housing"
    return render_template("housing.html", pred_form = price, title= title)
    
@app.route('/london', methods=["POST", "GET"])
def london():
    pkl_filename = "GbFinalLabel_model.pkl"
    with open(pkl_filename, 'rb') as file:
        model = pickle.load(file)

    map = folium.Map(location=[51.509865, -0.118092], tiles="OpenStreetMap", zoom_start=10.5)
    price = -1
    if request.method == "POST":
        lat_form = request.form['lat']
        long_form = request.form['long']
        zip = PostalCodeToLable(request.form['inputzip'])
        bed = int(request.form['inputbed'])
        bath = int(request.form['inputbath'])
        recep = int(request.form['inputRecep'])
        houseType = HouseTypeToLable(request.form['inputHouseType'])
        sqft = int(request.form['inputsq'])
        distCenter = distanceToLondon(lat_form, long_form)
        crime = getCrime(request.form['inputzip'])
        distHosp = distanceToHospital(lat_form, long_form)
        distSub = distanceToSubway(lat_form, long_form)
        distSchool = distanceToSchool(lat_form, long_form)
        

        data={'HouseType': houseType,'Areainsqft':sqft,'No.ofBedrooms': bed,'No.ofBathrooms': bath,'No.ofReceptions':recep,
                    'distance_to_london':distCenter,'NCrime':crime, 'DisToHospital':distHosp, 'DisToSubway':distSub, 'DisToShool':distSchool, 'PostalCode':zip}
        
        print(data)
        # Create DataFrame
        df = pd.DataFrame(data, index=[0])
        pred_price_form = model.predict(df).round(1)
        price = pred_price_form[0]
        
        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>House type: {houseType}<br>Sqft: {sqft}sq<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Pred. price: {price}£</i>"
        iframe = folium.IFrame(str, width=260, height=120)
        pop = folium.Popup(iframe, max_width=300)
        folium.Marker([lat_form, long_form], popup=pop, tooltip="Your house",
                      icon=folium.Icon(color='green', icon='home', prefix='fa')).add_to(map)

    style = {
        "fillOpacity": 0.1,
    }

    with open('london_boroughs.json') as json_file:
        london = json.load(json_file) #url = "https://skgrange.github.io/www/data/london_boroughs.json"

    folium.GeoJson(london, name="london", style_function= lambda x : style, tooltip=folium.features.GeoJsonTooltip(fields=['name',],sticky=False, labels=False, localize=True)).add_to(map)
    folium.LayerControl().add_to(map)

    #adding 100 random pois to the map
    poi = pd.read_csv("POI_London.csv")
    i = 0
    pos_vector = []
    while(True):
        index = randint(0, 28205)
        if index in pos_vector:
            continue
        pos_vector.append(index)
        row = poi.iloc[index]
        cm = folium.CircleMarker(location=[row.lat, row.long], radius=5,tooltip=row.name, fill=True, fill_color='lightblue', color='grey', fill_opacity=0.7)
        map.add_child(cm)
        i += 1
        if i == 50:
            break
    
    data = pd.read_csv('LondonFinalLable.csv')
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

        x= data.iloc[[i]]
        x = x[['HouseTypeLabel','Areainsqft','NoofBedrooms','NoofBathrooms','NoofReceptions',
                    'distance_to_london','NCrime', 'DisToHospital', 'DisToSubway', 'DisToShool', 'PostalCodeLabel']]


        pred_price = model.predict(x).round(1)
        str = f"<i style='font-family: Helvetica, sans-serif; line-height: 1.6;'>Type: {houseType}<br>Sqft: {sqft}sq<br>N beds: {bed}<br>N bath: {bath}<br>Distance to downtown: {round(distCenter,1)}km<br>Price: {real_price}£<br>Pred. price: {pred_price[0]}£</i>"

        iframe = folium.IFrame(str, width=260, height=120)
        pop = folium.Popup(iframe, max_width=300)
        folium.Marker([lat, long], popup=pop, tooltip=tooltip, icon=folium.Icon(color='cadetblue', icon='home', prefix='fa')).add_to(map)
        count += 1
        if count == 100:
            break

    map.save("templates/map.html")
    title = "London Housing"
    postalcode = pd.read_csv('PostCodeLabel.csv')
    post = postalcode['Postcode'].tolist()
    
    return render_template("housing.html", pred_form = price, title= title, postal = post)

@app.route('/map')
def map():
    return render_template('map.html')


if __name__ == '__main__':
    app.run(debug=True)
