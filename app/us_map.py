from flask import render_template
from app import app
import pandas as pd
import plotly.graph_objects as go

@app.route('/')
@app.route('/us_map')
def us_map():
    # Add code to connect to database and get data
    
    
    #states = pd.DataFrame()
    
    # Creating text for hover boxes
    #for col in states.columns:
    #     states[col] = states[col].astype(str)
    
    #states['text'] = 'State: ' + states['state_name'] + ', ' + states['state_abbreviation'] + '<br>' + \
    #     'Capital: ' + states['capital'] + '<br>' + \
    #     'Total Population: ' + states['total_population'] + '<br>' + \
    #     'Total Housing Units: ' + states['total_housing_units'] + '<br>' + \
    #     'Occupied Housing Units: ' + states['occupied_housing_units'] + ' (' + states['percent_occupied'] + '%)' + '<br>' + \
    #     'Vacant Housing Units: ' + states['vacant_housing_units'] + ' (' + states['percent_vacant'] + '%)' + '<br>' + \
    #     'Attraction: ' + states['attraction']
    
    # Creating heat map
    fig = go.Figure(data=go.Choropleth(
    #     locations=states['state_abbreviation'],
    #     z=states['total_population'].astype(float),
         locationmode='USA-states'))
    #     colorscale='Reds',
    #     text=states['text']))
    
    fig.update_layout(geo_scope='usa')
    
    return render_template('us_map.html', fig=fig)
