from flask import render_template, request
from app import app
import pyodbc
import pandas as pd
import plotly.graph_objects as go
from plotly.callbacks import Points
from urllib.request import urlopen
import json

# Connecting to database
server = 'statefinder.database.windows.net'
database= 'LivingWage'
username = 'statefinder'
password = '{FAll2022}'
driver = '{ODBC Driver 18 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+
                      ';PORT=1433;DATABASE='+database+';UID='+username+
                      ';PWD='+ password)
cursor = conn.cursor()

@app.route('/')
@app.route('/us_map', methods=['GET', 'POST'])
def us_map():
    
    # Getting state data
    q = ("SELECT * FROM state_descriptions;")
    states = pd.DataFrame()
    states = pd.read_sql_query(q, conn)
    
    # Formatting state hover text
    states['heat_value'] = states['total_population']

    for i in range(len(states)):
        states['total_population'][i] \
            = '{:,}'.format(int(states['total_population'][i]))
        states['total_housing_units'][i] \
            = '{:,}'.format(int(states['total_housing_units'][i]))
        states['occupied_housing_units'][i] \
            = '{:,}'.format(int(states['occupied_housing_units'][i]))
        states['vacant_housing_units'][i] \
            = '{:,}'.format(int(states['vacant_housing_units'][i]))

    for col in states.columns:
        states[col] = states[col].astype(str)

    states['text'] = 'State: ' + states['state_name'] + '<br>' + \
        'Capital: ' + states['capital'] + '<br>' + \
        'Total Population: ' + states['total_population'] + '<br>' + \
        'Total Housing Units: ' + states['total_housing_units'] + '<br>' + \
        'Occupied Housing Units: ' + states['occupied_housing_units'] + ' (' + \
            states['percent_occupied'] + '%)' + '<br>' + \
        'Vacant Housing Units: ' + states['vacant_housing_units'] + ' (' + \
            states['percent_vacant'] + '%)' + '<br>' \
        'Attraction: ' + states['attraction']
    
    # Creating us map
    fig = go.Figure(go.Choropleth(
        locations=states['state_abbreviation'], 
        z=states['heat_value'].astype(float).astype(int), 
        locationmode='USA-states', 
        colorscale='Oranges', 
        colorbar_title = 'Population', 
        text=states['text']))
    fig.update_layout(geo_scope='usa')    
    
    return render_template('us_map.html', fig=fig)

@app.route('/')
@app.route('/state_map', methods=['GET', 'POST'])
def state_map():
    
    # Getting metro area data
    q = ("SELECT * FROM metro_area_descriptions;")
    metro_areas = pd.DataFrame()
    metro_areas = pd.read_sql_query(q, conn)
    
    # Getting geojson
    with urlopen('https://raw.githubusercontent.com/annednguyen00/CSC490/main/metro_micro.json') as response:
        metro_micro = json.load(response)
        
    # Formatting metro area hover text
    metro_areas['heat_value'] = metro_areas['total_population']
    metro_areas['metro_area_id'] = metro_areas['metro_area_name']
    metro_areas['metro_area_name'] \
        = metro_areas['metro_area_name'].str.split(', ', expand=True)[0]

    for i in range(len(metro_areas)):
        metro_areas['total_population'][i] \
            = '{:,}'.format(int(metro_areas['total_population'][i]))
        metro_areas['total_housing_units'][i] \
            = '{:,}'.format(int(metro_areas['total_housing_units'][i]))
        metro_areas['occupied_housing_units'][i] \
            = '{:,}'.format(int(metro_areas['occupied_housing_units'][i]))
        metro_areas['vacant_housing_units'][i] \
            = '{:,}'.format(int(metro_areas['vacant_housing_units'][i]))

    for col in metro_areas.columns:
        metro_areas[col] = metro_areas[col].astype(str)

    metro_areas['text'] = 'Metro Area: ' + metro_areas['metro_area_name'] + '<br>' + \
        'Total Population: ' + metro_areas['total_population'] + '<br>' + \
        'Total Housing Units: ' + metro_areas['total_housing_units'] + '<br>' + \
        'Occupied Housing Units: ' + metro_areas['occupied_housing_units'] + ' (' + \
            metro_areas['percent_occupied'] + '%)' + '<br>' + \
        'Vacant Housing Units: ' + metro_areas['vacant_housing_units'] + ' (' + \
            metro_areas['percent_vacant'] + '%)'
            
    # Getting selected state
    selected_state = request.form['states']
    
    # Creating state map
    fig2 = go.Figure(go.Choropleth(
        geojson=metro_micro, 
        locations=metro_areas[metro_areas['state_abbreviation'] 
                              == selected_state].metro_area_id, 
        featureidkey='properties.NAME', 
        z=(metro_areas[metro_areas['state_abbreviation'] 
                       == selected_state].heat_value).astype(float).astype(int), 
        colorscale='Oranges', 
        colorbar_title = 'Population', 
        text=metro_areas[metro_areas['state_abbreviation'] 
                         == selected_state].text))
    fig2.update_geos(fitbounds='locations')
    
    return render_template('state_map.html', fig2=fig2)

conn.close