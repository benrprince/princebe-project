#############################################
# Author: Ben Prince
# Date: 5/10/2021
# CS_493 Assignment 7
############################################

# Google and Flask imports
from flask import Flask, render_template, request, redirect, session
from google.cloud import datastore
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_request

# Other imports
import constants
import requests
import random
import json

app = Flask(__name__)
client = datastore.Client()
app.config['SECRET_KEY'] = 'sessionsecret'

@app.route('/')
def index():
    return "Hello World"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)