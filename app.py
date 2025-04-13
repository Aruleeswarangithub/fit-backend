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
    # Aggregate all step counts
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

    for bucket in fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    bpm = value.get("fpVal", 0)
                    if 30 <= bpm <= 200:  # Valid heart rate range
                        total += bpm
                        count += 1
                        latest_heart_rate = bpm  # Track the latest HR

    # Return the average heart rate or fallback to the latest valid reading
    if latest_heart_rate:
        avg_heart_rate = round(total / count) if count else latest_heart_rate
    else:
        avg_heart_rate = 62  # Default if no valid heart rate is found

    return jsonify({"average_heart_rate": avg_heart_rate})


@app.route("/calories", methods=["POST"])
def get_calories():
    data = request.json
    fit_data = fetch_google_fit_data(
        data["access_token"], "com.google.calories.expended", data["start_time"], data["end_time"]
    )

    total_calories = 0.0
    # Aggregate all calorie values (active and resting)
    for bucket in fit_data.get('bucket', []):
        for dataset in bucket['dataset']:
            for point in dataset['point']:
                for value in point['value']:
                    total_calories += value.get("fpVal", 0.0)

    return jsonify({"total_calories": round(total_calories)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
