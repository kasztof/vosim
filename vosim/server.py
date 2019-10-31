from flask import Flask
from dash import Dash

EXTERNAL_STYLESHEETS = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

flask_app = Flask(__name__)
app = Dash(__name__, server=flask_app, url_base_pathname='/', external_stylesheets=EXTERNAL_STYLESHEETS,
           assets_url_path='/vosim/assets') 
