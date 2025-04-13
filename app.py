from flask import Flask, request, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

GOOGLE_FIT_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

def fetch_google_fit_data(access_token, data_type_name, start_time, end_time):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "aggregateBy": [{"dataTypeName": data_type_name}],
        "bucketByTime": {"durationMillis": 1800000},  # Aggregating data every 30 minutes
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }

    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()

@app.route("/steps", methods=["POST"])
def get_steps():
    data = request.json
    now = datetime.now()
    start_time = int((now - timedelta(days=1)).timestamp() * 1000)  # Last 24 hours
    end_time = int(now.timestamp() * 1000)  # Current time
    response = fetch_google_fit_data(data["access_token"], "com.google.step_count.delta", start_time, end_time)
    return jsonify(response)

@app.route("/heart_rate", methods=["POST"])
def get_heart_rate():
    data = request.json
    now = datetime.now()
    start_time = int((now - timedelta(days=1)).timestamp() * 1000)  # Last 24 hours
    end_time = int(now.timestamp() * 1000)  # Current time
    response = fetch_google_fit_data(data["access_token"], "com.google.heart_rate.bpm", start_time, end_time)
    return jsonify(response)

@app.route("/calories", methods=["POST"])
def get_calories():
    data = request.json
    now = datetime.now()
    start_time = int((now - timedelta(days=1)).timestamp() * 1000)  # Last 24 hours
    end_time = int(now.timestamp() * 1000)  # Current time
    response = fetch_google_fit_data(data["access_token"], "com.google.calories.expended", start_time, end_time)
    return jsonify(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
