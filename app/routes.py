from flask import Flask, render_template, request, redirect, flash
from app import app
import os
import pandas as pd
import numpy as np
import pyodbc
import json
import requests
import plotly.express as px
import geopandas as gpd
from urllib.request import urlopen
from .forms import ContactForm
from flask_mail import Message, Mail
import pymssql  

#connecting to the data base constants
#server = 'statefinder.database.windows.net'
#database = 'LivingWage'
#username = 'statefinder'
#password = '{FAll2022}'
#driver = '{ODBC Driver 17 for SQL Server}'
#conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=tcp:' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)
conn = pymssql.connect(server='statefinder.database.windows.net', user='statefinder@statefinder.database.windows.net', password='FAll2022', database='LivingWage')
cursor = conn.cursor()

#creating the squeries
q1 = ("SELECT * FROM OCCUPATIONS;")
q2 = ("SELECT * FROM One_Adult;")
q3 = ("SELECT * FROM Two_Adults_One_Working;")
q4 = ("SELECT * FROM Two_Adults_Both_Working;")

#creating the data frames
occ = pd.DataFrame()
one_adult = pd.DataFrame()

#saving sql tables as panda dataframes
occ = pd.read_sql_query(q1, conn)
one_adult = pd.read_sql_query(q2, conn)
two_adults_1w = pd.read_sql_query(q3, conn)
two_adults_2w = pd.read_sql_query(q4, conn)
conn.close

# Create flask mail connection to email
mail = Mail()

SECRET_KEY = os.urandom(32)

app.config['SECRET_KEY'] = SECRET_KEY
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'sfmssgbot@gmail.com'
app.config["MAIL_PASSWORD"] = 'zpklgtbnupcdvmmy'
 
mail.init_app(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True
@app.route('/')
@app.route('/index', methods=['GET'])

#sending occupations list to index
def index():
 
    send = occ['OCC_TITLE']
    #sending data to html files
    return render_template('index.html', occupations = send)

@app.route('/')
@app.route('/about', methods=['GET'])
def about():
    #render about page
    return render_template('about.html')

#render contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm()
  
  # Check if all fields filled
  if request.method == 'POST':
    if form.validate() == False:
        flash('All fields are required.')
        return render_template('contact.html', form=form)
    
    # Auto send email, send email to help email
    else:
      automsg = Message(subject='We received your contact request', sender='sfmssgbot@gmail.com', recipients=[form.email.data])
      automsg.body = """
      %s,
      Thank you for reaching out to the State Finder team. We have received your message regarding %s and will be in contact with you shortly.
      Yours,
      State Finder Admins
      """ % (form.name.data, form.subject.data)
      mail.send(automsg)

      msg = Message(form.subject.data, sender='sfmssgbot@gmail.com', recipients=['statefinderhelp@gmail.com'])
      msg.body = """
      From: %s
      Email:  %s;
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      mail.send(msg)
      
      return render_template('contact.html', success=True)
        
  elif request.method == 'GET':
    return render_template('contact.html', form=form)


@app.route('/')
@app.route('/populateMap', methods=['POST'])
def populateMap():
    
    #getting data from index form
     occupation = request.form['occSelect']
     level = request.form['levelSelect']
     adult_num = request.form['adultSelect']
     kid_num = request.form['kidSelect']

    
     occ.fillna(0, inplace=True)

    #getting the users wages per level and occupation from table
     if level == "Entry level":
        s = pd.DataFrame(occ.loc[occ['OCC_TITLE'] == occupation])
        user_wage = s['A_PCT10']
     elif level == "Intermediate level":
        s = pd.DataFrame(occ.loc[occ['OCC_TITLE'] == occupation])
        user_wage = s['A_PCT25']
     else:
        s = pd.DataFrame(occ.loc[occ['OCC_TITLE'] == occupation])
        user_wage = s['A_PCT75']

     if (user_wage == 0).any() :
         fig = "No Data"
         b = 4
     else:
         #selects table based on number of working adults
         if adult_num == "1 adult":
             adult = one_adult
         elif adult_num == "2 adults, 1 working":  
             adult = two_adults_1w
         else:
             adult = two_adults_2w
     
         #selects metro wage based on kids
         if kid_num == "0 children":
              metro_wage = adult[['metro_area','state_name','zero_kids_year']]
         elif kid_num == "1 child":
              metro_wage = adult[['metro_area','state_name','one_kids_year']]
         elif kid_num == "2 children":
              metro_wage = adult[['metro_area','state_name','two_kids_year']]
         else:
             metro_wage = adult[['metro_area','state_name','three_kids_year']]
    
       
         #calculated difference between user wage and livable wage.
         b = calculate_difference(metro_wage,user_wage)
         t = b.to_html()
    
     
  

         #Generating shapefiles for map generation

         #getting geojson file
         url = 'https://raw.githubusercontent.com/Alyiahp/geojsons/main/cb_2018_us_cbsa_20m.geojson'
         f = requests.get(url)
         data = f.json()
  
         areas_geo = []
         tmp = b.set_index('ID')

       #Looping over GeoJSON file
         for area in data['features']:
    
          area_name = area['properties']['NAME'] 
    
        # Checking if that area is in the dataset
          if area_name in tmp.index:
        
            # Getting information from both GeoJSON file and dataFrame
             geometry = area['geometry']
        
            # Adding 'id' 
             areas_geo.append({
                'type': 'Feature',
                'geometry': geometry,
                'id':area_name
            })
          
         metro_json = {'type': 'FeatureCollection', 'features': areas_geo}
         
         #if max residual income is negative all reds for the map
         if b['Residual Income'].max() < 0:
             fig = px.choropleth(b, geojson = metro_json, locations='ID', color='Residual Income',                  
                               range_color=(b['Residual Income'].min(),b['Residual Income'].max()),
                               color_continuous_scale= 'Reds_r',                              
                               scope="usa",
                               labels={'Residual Income':'Leftover Income'})
             fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

         #if minimum residual income is positive then all greens for the map
         elif b['Residual Income'].min() >0:
              fig = px.choropleth(b, geojson = metro_json, locations='ID', color='Residual Income',                  
                               range_color=(b['Residual Income'].min(),b['Residual Income'].max()),
                               color_continuous_scale='Greens_r',
                               color_continuous_midpoint=0,
                               scope="usa",
                               labels={'Residual Income':'Leftover Income'})
              fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

              # else the map has a combination of green and red
         else:
              average = b["Residual Income"].mean()
              fig = px.choropleth(b, geojson = metro_json, locations='ID', color='Residual Income',                  
                               range_color=(b["Residual Income"].mean(),0),
                               color_continuous_scale=['red','green'],
                               scope="usa",
                               labels={'Residual Income':'Leftover Income'})
              fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
       

     
     return render_template('populateMap.html', table = b, fig = fig)



def calculate_difference(metro_wage, user_wage):
    #Making ID match geogson file names
    metro_wage['metro_area'] = metro_wage['metro_area'].apply(lambda x: x.split('_')[0])
    metro_wage['ID'] = metro_wage['metro_area'].fillna('') + ', ' + metro_wage['state_name'].fillna('')
   
    #calculating value
    map_values = pd.DataFrame(metro_wage['ID'])
    map_values['Residual Income'] = int(user_wage) - metro_wage.iloc[:,2].astype(int)
    map_values =  map_values.sort_values(by=['Residual Income'], ascending=False)
    map_values = map_values.reset_index(drop=True)

    return map_values


@app.route('/')
@app.route('/google_login', methods=['GET', 'POST'])

def google_login():
    return render_template('google_login.html')