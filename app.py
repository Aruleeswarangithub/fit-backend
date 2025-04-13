from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GOOGLE_FIT_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

def fetch_google_fit_data(access_token, data_type_name, start_time, end_time):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "aggregateBy": [{"dataTypeName": data_type_name}],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }

    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()


@app.route("/steps", methods=["POST"])
def get_steps():
    data = request.json
    return jsonify(fetch_google_fit_data(
        data["access_token"], "com.google.step_count.delta", data["start_time"], data["end_time"]
    ))


@app.route("/heart_rate", methods=["POST"])
def get_heart_rate():
    data = request.json
    return jsonify(fetch_google_fit_data(
        data["access_token"], "com.google.heart_rate.bpm", data["start_time"], data["end_time"]
    ))


@app.route("/calories", methods=["POST"])
def get_calories():
    data = request.json
    return jsonify(fetch_google_fit_data(
        data["access_token"], "com.google.calories.expended", data["start_time"], data["end_time"]
    ))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
