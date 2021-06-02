#############################################
# Author: Ben Prince
# Date: 06/07/2021
# Functions to make main.py a little less cluttered
############################################
from google.cloud import datastore
from flask import request
import constants

client = datastore.Client()

# Functions for the User entity / authentication
def patch_stadium(content, stadium):
    """ Function handles the patch request
    method for stadiums"""
    
    name = ""
    sport = ""
    location = ""
    capacity = 0

    if "name" in content:
        name = content["name"]
    else:
        name = stadium["name"]

    if "sport" in content:
        sport = content["sport"]
    else:
        sport = stadium["sport"]

    if "location" in content:
        location = content["location"]
    else:
        location = stadium["location"]
    
    if "capacity" in content:
        capacity = content["capacity"]
    else:
        capacity = stadium["capacity"]

    stadium.update({"name": name, "sport": sport, "location": location,
        "capacity": capacity})
    client.put(stadium)
    stadium["id"] = stadium.key.id
    url = request.url_root + '/stadiums/' + str(stadium["id"])
    stadium["self"] = url

    return stadium