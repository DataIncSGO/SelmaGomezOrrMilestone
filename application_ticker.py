# Author: Selma Gomez Orr <selmagomezorrds@gmail.com> December 9, 2015

##########################################################################
## Imports for application
##########################################################################

import os
from flask import Flask, render_template, request, redirect

import requests
import pandas as pd
from datetime import datetime

from bokeh.plotting import figure
#from bokeh.resources import CDN
from bokeh.embed import components

##########################################################################
## Modules
##########################################################################

app_ticker = Flask(__name__)

#Variable to hold the stock ticker input from user.
STOCK=''       

#Module which obtains user input, gets stock data from Quandl, and creates a graph.
@app_ticker.route('/index_ticker', methods=['GET', 'POST'])
def index_ticker():
    if request.method == 'GET':
        #Go to user info html for getting input.
        return render_template('ticker_info.html')
    else:
        STOCK = request.form['name_ticker']
        
        #Get the stock closing price data for the requested stock.
        api_url = 'https://www.quandl.com/api/v1/datasets/WIKI/%s.json' % STOCK
        session = requests.Session()
        session.mount('http://', requests.adapters.HTTPAdapter(max_retries=3))
        raw_data = session.get(api_url)
        
        #Turn request object into json and extract the headers and the stock data.
        data = raw_data.json()
        headers = data["column_names"]
        data_list = data["data"]
        
        #Put data into a pandas dataframe and format the date string to a date.
        data_df = pd.DataFrame(data_list, columns = headers)
        data_df['Date'] = pd.to_datetime(data_df['Date'], format='%Y-%m-%d')
        
        #Define the data points for the graph as the last month, or thirty days.
        x = data_df['Open'][:30]
        y = data_df['Close'][:30]
        
        #Define the graph.        
        p = figure(title="Data from Quandl WIKI set", x_axis_label='Date', x_axis_type='datetime', y_axis_label='Price')
        
        p.line(x, y, legend=STOCK+': Close', line_width=2)
        
        #Create graph components.
        script, div = components(p)
        
        #Go to graph html for display.
        return render_template('graph.html', symb=STOCK, script=script, div=div)

#Module redirects the user back to the input page for a new request.
@app_ticker.route('/next_ticker')
def next_ticker():
    return redirect('/index_ticker') 

##########################################################################
## Program 
##########################################################################
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app_ticker.run(host='0.0.0.0', port=port)
    
