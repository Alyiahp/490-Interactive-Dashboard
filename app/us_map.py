from flask import render_template
from app import app
import pyodbc
import pandas as pd
import plotly.graph_objects as go

@app.route('/')
@app.route('/us_map')
def us_map():
    
    # Connecting to the database
    server = 'statefinder.database.windows.net'
    database= 'LivingWage'
    username = 'statefinder'
    password = '{FAll2022}'
    driver = '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='
                          +database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()
    
    # Converting queries to dataframe
    q = ("SELECT * FROM state_descriptions;")
    states = pd.DataFrame()
    states = pd.read_sql_query(q, conn)
    conn.close
    
    # Creating text for hover boxes
    for col in states.columns:
         states[col] = states[col].astype(str)
    
    states['text'] = 'State: ' + states['state_name'] + '<br>' + \
                     'Capital: ' + states['capital'] + '<br>' + \
                     'Total Population: ' + states['total_population'] + '<br>' + \
                     'Total Housing Units: ' + states['total_housing_units'] + '<br>' + \
                     'Occupied Housing Units: ' + states['occupied_housing_units'] + \
                         ' (' + states['percent_occupied'] + '%)' + '<br>' + \
                     'Vacant Housing Units: ' + states['vacant_housing_units'] + \
                         ' (' + states['percent_vacant'] + '%)' + '<br>' + \
                     'Attraction: ' + states['attraction']
    
    # Creating heat map
    fig = go.Figure(data=go.Choropleth(
         locations=states['state_abbreviation'],
         z=states['total_population'].astype(float),
         locationmode='USA-states',
         colorscale= [[0, 'rgb(255,0,0)'], 
                      [0.5, 'rgb(255,255,0)'], 
                      [1, 'rgb(0,128,0)']],
         text=states['text']))
    
    fig.update_layout(geo_scope='usa')
    
    return render_template('us_map.html', fig=fig)
