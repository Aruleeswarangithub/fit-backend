from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/get_fit_data", methods=["POST"])
def get_fit_data():
    data = request.json
    access_token = data.get("access_token")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    body = {
        "aggregateBy": [
            {
                "dataTypeName": "com.google.step_count.delta"
            }
        ],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": data["start_time"],
        "endTimeMillis": data["end_time"]
    }

    response = requests.post(url, headers=headers, json=body)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
