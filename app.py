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
        "bucketByTime": {"durationMillis": 86400000},  # 1 day (24 hours)
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }

    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()


@app.route("/steps", methods=["POST"])
def get_steps():
    data = request.json
    fit_data = fetch_google_fit_data(
        data["access_token"], "com.google.step_count.delta", data["start_time"], data["end_time"]
    )

    total_steps = 0
    for bucket in fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    total_steps += value.get("intVal", 0)

    return jsonify({"steps": total_steps})


@app.route("/heart_rate", methods=["POST"])
def get_heart_rate():
    data = request.json
    fit_data = fetch_google_fit_data(
        data["access_token"], "com.google.heart_rate.bpm", data["start_time"], data["end_time"]
    )

    total = 0
    count = 0
    latest_heart_rate = None

    # Iterate over data to get heart rate readings
    for bucket in fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    bpm = value.get("fpVal", 0)
                    if 30 <= bpm <= 200:  # Valid heart rate range
                        total += bpm
                        count += 1
                        latest_heart_rate = bpm  # Track the latest HR

    # If no valid HR data, fallback to the latest HR reading
    if count > 0:
        avg_heart_rate = round(total / count)
    elif latest_heart_rate is not None:
        avg_heart_rate = latest_heart_rate  # Use the latest heart rate value
    else:
        avg_heart_rate = 62  # Default fallback HR if no data found

    return jsonify({"average_heart_rate": avg_heart_rate})


@app.route("/calories", methods=["POST"])
def get_calories():
    data = request.json

    # Fetch active calories
    active_fit_data = fetch_google_fit_data(
        data["access_token"], "com.google.calories.expended", data["start_time"], data["end_time"]
    )

    # Fetch resting calories
    resting_fit_data = fetch_google_fit_data(
        data["access_token"], "com.google.calories.bmr", data["start_time"], data["end_time"]
    )

    active_calories = 0.0
    resting_calories = 0.0

    # Aggregate active calories
    for bucket in active_fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    active_calories += value.get("fpVal", 0.0)

    # Aggregate resting calories
    for bucket in resting_fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    resting_calories += value.get("fpVal", 0.0)

    # Total calories as sum of active and resting calories
    total_calories = active_calories + resting_calories

    # Ensure calories are being returned correctly
    return jsonify({
        "active_calories": round(active_calories),
        "resting_calories": round(resting_calories),
        "total_calories": round(total_calories)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
