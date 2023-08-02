import functions_framework
from flask import jsonify
from time import time
import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

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

    dt = int(time())
    temp = data['iaqi']['t']['v']
    pressure = data['iaqi']['p']['v']
    wind = data['iaqi']['w']['v']
    weather = {"timestamp":  dt,  "temp": temp, "pressure": pressure, "wind": wind}

    return weather

@functions_framework.http
def main(request):
    collection_ref = db.collection('weather')
    data = get_weather()
    collection_ref.add(data)
    return jsonify({"success": True, "message": "Collection created and dummy data added"})