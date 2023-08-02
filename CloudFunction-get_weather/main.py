import functions_framework
import requests
import os
from time import time
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

PROJECT_ID = 'testgke-391408'
cred = credentials.ApplicationDefault()
default_app = firebase_admin.initialize_app(cred, {
  'projectId': PROJECT_ID,
})
db = firestore.client()


def get_weather():
    """
    Gibt die Daten einer bestimmten Wetterstation zurück. Die Wetterstation wird mit Hilfe einer ID angegeben
    """
    AQIN_KEY = "e6e52e8fc683d9fcc03235abe9db9d8bc101230b"
    UmweltstationID = "6143"
    response = requests.get(
        f"https://api.waqi.info/feed/@{UmweltstationID}/?token={AQIN_KEY}"
    )
    if response.json()['data'] == "Unknown station":
        print("Fehler bei Station")
        return {"error": "Es wurde keine Umweltstation gefunden"}
    
    data = response.json()['data']

    dt = str(int(time()))
    temp = data['iaqi']['t']['v']
    pressure = data['iaqi']['p']['v']
    wind = data['iaqi']['w']['v']
    weather = {"timestamp":  dt,  "temp": temp, "pressure": pressure, "wind": wind}

    return weather

def get_weather_from_db(timestamp):
    # target_timestamp = datetime.datetime.fromtimestamp(int(timestamp)) # Convert to datetime object
    
    # # # Query for the first document with timestamp less than or equal to the target
    # # closest_below = db.collection('weather').where('timestamp', '<=', timestamp).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(1).stream()
    
    # # # Query for the first document with timestamp greater than the target
    # # closest_above = db.collection('weather').where('timestamp', '>', timestamp).order_by('timestamp', direction=firestore.Query.ASCENDING).limit(1).stream()
    
    # # # Extract documents from query results
    # # closest_below = [doc.to_dict() for doc in closest_below]
    # # closest_above = [doc.to_dict() for doc in closest_above]

    # # # Calculate distances to the target timestamp
    # # distance_below = abs(closest_below[0]['timestamp'] - timestamp) if closest_below else float('inf')
    # # distance_above = abs(closest_above[0]['timestamp'] - timestamp) if closest_above else float('inf')
    
    # # # Return the document with the closest timestamp value
    # # if distance_below <= distance_above:
    # #     return closest_below[0] if closest_below else None
    # # else:
    # #     return closest_above[0] if closest_above else None



    # doc = db.collection("weather")
    # final_result = None

    # # query = doc.where("timestamp", ">=", int(timestamp)).order_by("timestamp", direction=firestore.Query.ASCENDING).limit(1)
    # query = doc.where("timestamp", ">=", int(timestamp)).order_by("timestamp", direction=firestore.Query.ASCENDING).limit(1).get()
    # results = query.stream()
    # for result in results:
    #     print('Final Rsult 2', result)
    #     final_result = result.to_dict()

    # if final_result is None:
    #     print('First result was None')
    #     query = doc.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    #     results = query.stream()
    #     for result in results:
    #         final_result = result.to_dict()

    # return final_result

    doc = db.collection("weather")
    final_result = None

    query = doc.where(filter=FieldFilter("timestamp", ">=", int(timestamp))).order_by("timestamp").limit(1)
    results = query.get()

    for result in results:
        print('Final Result 1', result.to_dict())
        final_result = result.to_dict()

    if final_result is None:
        print('First result was None')
        query = doc.order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
        results = query.get()
        for result in results:
            print('Final Result 2', result.to_dict())
            final_result = result.to_dict()

    return final_result





@functions_framework.http
def main(request):
    print("MOIN")
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_args and 'timestamp' in request_args:
        return get_weather_from_db(request_args['timestamp'])
    else:
        return get_weather()

    # if request_json and 'name' in request_json:
    #     name = request_json['name']
    # elif request_args and 'name' in request_args:
    #     name = request_args['name']
    # else:
    #     name = str(get_weather())
    # return 'Hello {}!'.format(name)
