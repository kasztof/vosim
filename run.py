import os

from vosim.app import app
from dotenv import load_dotenv
from os.path import join, dirname

DOTENV_PATH = join(dirname(__file__), '.env')
load_dotenv(DOTENV_PATH)

PORT = os.environ.get('PORT')

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=PORT, debug=False)