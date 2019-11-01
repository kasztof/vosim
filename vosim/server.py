from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc


flask_app = Flask(__name__)
app = Dash(__name__, server=flask_app, url_base_pathname='/', external_stylesheets=[dbc.themes.BOOTSTRAP],
           assets_url_path='/vosim/assets') 
