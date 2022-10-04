#from flask import flask
from flask import render_template
from app import app
import pandas as pd
import numpy as np
import pyodbc


#app.config['TEMPLATES_AUTO_RELOAD'] = True
@app.route('/')
@app.route('/index')
def index():

    #connecting to the data base
    server = 'statefinder.database.windows.net'
    database= 'LivingWage'
    username = 'statefinder'
    password = '{FAll2022}'
    driver = '{ODBC Driver 17 for SQL Server}'
    conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = conn.cursor()

    #queries
    q = ("SELECT * FROM OCCUPATIONS_TWO;")

    occ = pd.DataFrame()

    #saving sql tables as panda dataframes
    occ = pd.read_sql_query(q, conn)
    conn.close
    
    #sending data to html files
    return render_template('index.html', data = occ)