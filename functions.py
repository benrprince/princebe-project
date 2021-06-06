#############################################
# Author: Ben Prince
# Date: 06/07/2021
# Functions to make main.py a little less cluttered
############################################
from google.cloud import datastore
from flask import request
import constants

client = datastore.Client()

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

def patch_ticket(content, ticket):
    """ Function handles the patch request
    method for tickets"""

    sport = ""
    event = ""
    location = ""
    date = ""

    if "sport" in content:
        sport = content["sport"]
    else:
        sport = ticket["sport"]

    if "event" in content:
        event = content["event"]
    else:
        event = ticket["event"]

    if "location" in content:
        location = content["location"]
    else:
        location = ticket["location"]
    
    if "date" in content:
        date = content["date"]
    else:
        date = ticket["date"]

    ticket.update({"sport": sport, "event": event, "location": location,
        "date": date})
    client.put(ticket)
    ticket["id"] = ticket.key.id
    url = request.url_root + '/ticket/' + str(ticket["id"])
    ticket["self"] = url

    return ticket


# Check for seat availability
def check_seat_availability(content):
    """Function checks for the seat availability
       for a given event"""
    
    query = client.query(kind=constants.tickets)
    results = list(query.fetch())

    for ticket in results:
        if (ticket["event"] == content["event"]) and \
            (ticket["date"] == content["date"]) and \
            (ticket["location"] == content["location"]):

            return False
        
        else:
            return True