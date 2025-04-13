from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

GOOGLE_FIT_URL = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"

def post_to_google_fit(access_token, aggregate_by, start_time, end_time):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "aggregateBy": aggregate_by,
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time,
        "endTimeMillis": end_time
    }
    response = requests.post(GOOGLE_FIT_URL, headers=headers, json=body)
    return response.json()

@app.route("/steps", methods=["POST"])
def get_steps():
    data = request.json
    result = post_to_google_fit(
        data["access_token"],
        [{"dataTypeName": "com.google.step_count.delta"}],
        data["start_time"],
        data["end_time"]
    )

    total_steps = 0
    for bucket in result.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                for val in point.get("value", []):
                    if "intVal" in val:
                        total_steps += val["intVal"]

    return jsonify({"steps": total_steps})

@app.route("/heart_rate", methods=["POST"])
def get_heart_rate():
    data = request.json
    result = post_to_google_fit(
        data["access_token"],
        [{"dataTypeName": "com.google.heart_rate.bpm"}],
        data["start_time"],
        data["end_time"]
    )

    hr_sum = 0
    count = 0
    for bucket in result.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                for val in point.get("value", []):
                    if "fpVal" in val and 30 <= val["fpVal"] <= 200:
                        hr_sum += val["fpVal"]
                        count += 1

    avg_hr = round(hr_sum / count) if count > 0 else 0
    return jsonify({"average_heart_rate": avg_hr})

@app.route("/calories", methods=["POST"])
def get_calories():
    data = request.json
    result = post_to_google_fit(
        data["access_token"],
        [
            {"dataTypeName": "com.google.calories.expended"},
            {"dataTypeName": "com.google.calories.bmr"}
        ],
        data["start_time"],
        data["end_time"]
    )

    total_calories = 0
    for bucket in result.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                for val in point.get("value", []):
                    if "fpVal" in val:
                        total_calories += val["fpVal"]

    return jsonify({"total_calories": round(total_calories)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
