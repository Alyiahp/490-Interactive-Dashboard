from flask import render_template
from app import app
import pandas as pd
import numpy as np

def testFunction():
    return 4


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Miguel'}
    x = pd.DataFrame(np.random.randn(20, 5))
    number = testFunction()
    return render_template('index.html', title='Home', user=user, data=x,number=number)