#############################################
# Author: Ben Prince
# Date: 06/07/2021
# CS_493 Final Project
############################################

# Google and Flask imports
from flask import Flask, render_template, request, redirect, session, make_response
from google.cloud import datastore
from google.oauth2 import id_token
from google.auth.transport import requests as google_auth_request

# Other imports
import constants
import functions
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

            # Get name
            f_name = info["names"][0]["givenName"]
            l_name = info["names"][0]["familyName"]

            # Get sub to create user entity
            req = google_auth_request.Request()
            idinfo = id_token.verify_oauth2_token(id_tok, req, CLIENT_ID)

            # Check if user already exists
            query = client.query(kind=constants.users)
            results = list(query.fetch())
            exists = 0

            for user in results:
                if user["sub"] == idinfo["sub"]:
                    exists = 1
            
            if exists == 0:
                # Initialize new user if user with the sub doesn't already exist
                new_user = datastore.entity.Entity(key=client.key(constants.users))
                new_user.update({"first name": f_name, "last name": l_name, "sub": idinfo["sub"],
                                "tickets": None})
                client.put(new_user)
                # add self link
                new_user["id"] = new_user.key.id

        return render_template("welcome-modal.html", f_name=f_name, l_name=l_name, token=id_tok)

    elif request.method == "POST":
        session['state'] = stateGenerator(10)

        return redirect("https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id="\
            + CLIENT_ID +"&redirect_uri="+ REDIRECT +"&scope=profile&state=" + str(session['state']))

    else:

        return render_template("welcome.html")

@app.route('/users', methods=["GET"])
def users_get():

    if request.method == "GET":
        query = client.query(kind=constants.users)
        results = list(query.fetch())

        for user in results:
            user["id"] = user.key.id

        return json.dumps(results)        # TODO: remove irrelevant fields

    else:
        return "Method not recognized"

@app.route('/stadiums', methods=["POST", "GET"])
def stadiums_post_get():

    if request.method == "POST":

        # Makes sure response has an application/json mimetype
        if request.is_json != True:
            res = make_response({"Error": "Request must be application/json"})
            res.mimetype = 'application/json'
            res.status_code = 415
            return res

        content = request.get_json()

        if ('name' not in content) or ('sport' not in content) or \
            ('location' not in content) or ('capacity' not in content):
            res = make_response({"Error": "The request object is missing at least one of the required attributes"})
            res.mimetype = 'application/json'
            res.status_code = 400
            return res

        
        # Create/add stadium to datastore
        new_stadium = datastore.entity.Entity(key=client.key(constants.stadiums))
        new_stadium.update({"name": content["name"], "sport": content["sport"], 
                            "location": content["location"], "capacity": content["capacity"]})
        client.put(new_stadium)
        new_stadium["id"] = new_stadium.key.id
        url = request.url_root + '/stadiums/' + str(new_stadium["id"])
        new_stadium["self"] = url

        return (new_stadium, 201)

    elif request.method == "GET":

        # Mimetype must be application/json
        if "application/json" in request.accept_mimetypes:
            
            # Pagination setup
            query = client.query(kind=constants.stadiums)
            q_limit = int(request.args.get('limit', '5'))
            q_offset = int(request.args.get('offset', '0'))
            l_iterator = query.fetch(limit=q_limit, offset=q_offset)
            pages = l_iterator.pages
            results = list(next(pages))
            stadium_count = len(results)

            if l_iterator.next_page_token:
                next_offset = q_offset + q_limit
                next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
            else:
                next_url = None

            for stadium in results:
                stadium["id"] = stadium.key.id
                url = request.url_root + '/stadiums/' + str(stadium["id"])
                stadium["self"] = url

            output = {"stadiums": results}
            output["count"] = stadium_count

            if next_url:
                output["next"] = next_url
            return json.dumps(output)

        else:
            res = make_response({"Error": "Requested unsupported content type"})
            res.mimetype = 'application/json'
            res.status_code = 406
            return res

    else:
        res = make_response({"Error": "Unknown request method or method not allowed"})
        res.mimetype = 'application/json'
        res.status_code = 405
        return res

@app.route('/stadiums/<sid>', methods=["GET", "PUT", "PATCH"])
def stadium_get(sid):
    if request.method == "GET":

        # get stadium from datastore
        key = client.key(constants.stadiums, int(sid))
        stadium = client.get(key=key)

        # return 404 if stadium doesn't exist
        if stadium == None:
            return ('{"Error": "No stadium with this stadium_id exists"}', 404)

        else:
            stadium["id"] = stadium.key.id
            url = request.url_root + '/stadiums/' + str(stadium["id"])
            stadium["self"] = url

        return json.dumps(stadium)

    elif request.method == "PUT":
        return

    elif request.method == "PATCH":

        stadium_key = client.key(constants.stadiums, int(sid))
        stadium = client.get(key=stadium_key)
        if stadium == None:
            return ('{"Error": "No stadium with this stadium_id exists"}',404)
        else:

            if request.is_json != True:
                res = make_response({"Error": "Request must be application/json"})
                res.mimetype = 'application/json'
                res.status_code = 415
                return res
            
            content = request.get_json()

            stadium = functions.patch_stadium(content, stadium)

            return (stadium, 200)

    else:
        return "Method not recognized"
         

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)