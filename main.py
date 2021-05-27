#############################################
# Author: Ben Prince
# Date: 06/07/2021
# CS_493 Final Project
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

# Set up Flask, datastore and secret key for session variables
app = Flask(__name__)
client = datastore.Client()
app.config['SECRET_KEY'] = 'sessionsecret'

@app.route('/')
def index():
    return "Please Navigate to /welcome"

@app.route('/welcome', methods=["GET", "POST"])
def welcome():

    if request.method == "GET":
        return render_template("welcome.html")

    elif request.method == "POST":
        return

    else:

        return render_template("welcome.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)