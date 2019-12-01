from flask import Flask
from dash import Dash
import dash_bootstrap_components as dbc


def init_server():
    flask_app = Flask(__name__)
    return Dash(__name__, server=flask_app,
           url_base_pathname='/',
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           assets_url_path='/vosim/assets') 


app = init_server()