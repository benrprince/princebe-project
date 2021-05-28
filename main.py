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

# Client Info for OAuth
CLIENT_ID = "375849959607-89c1t67ikbte0qvgeitaq64brafgptjj.apps.googleusercontent.com"
CLIENT_SECRET = "B7YzLUIPg00S31UuX9tl8a4B"
REDIRECT = "http://localhost:8080/welcome"

def stateGenerator(n):
    start = 10**(n-1)
    end = (10**n) - 1
    return random.randint(start, end)

@app.route('/')
def index():
    return "Please Navigate to /welcome"

@app.route('/welcome', methods=["GET", "POST"])
def welcome():

    if request.method == "GET":

        # Check for state
        if request.args.get("state") is None:
            return render_template('welcome.html')

        # If state given in url doesn't match session state, render home
        if request.args.get("state") != str(session['state']):
            print("ERROR: Session variable did not match")
            return render_template('welcome.html')

        code = request.args.get("code")
        if code is not None:

            # request for the access token
            response = requests.post("https://oauth2.googleapis.com/token?code="+ code +\
            "&client_id="+ CLIENT_ID +"&client_secret="+ CLIENT_SECRET +"&redirect_uri=" \
                + REDIRECT +"&grant_type=authorization_code")

            token_json = response.json()
            token = token_json["access_token"]
            id_tok = token_json["id_token"]

            # Send Access token to get information
            header = {"Authorization": "Bearer "+ token}
            req_url = "https://people.googleapis.com/v1/people/me?personFields=names"
            req = requests.get(req_url, headers=header)
            info = req.json()

            f_name = info["names"][0]["givenName"]
            l_name = info["names"][0]["familyName"]

        return render_template("welcome-modal.html")

    elif request.method == "POST":
        session['state'] = stateGenerator(10)

        return redirect("https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id="\
            + CLIENT_ID +"&redirect_uri="+ REDIRECT +"&scope=profile&state=" + str(session['state']))

    else:

        return render_template("welcome.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)