# Flask backend (optimized real-time Google Fit fetcher)
from flask import Flask, request, jsonify
import requests
import time

app = Flask(__name__)

BASE_URL = 'https://www.googleapis.com/fitness/v1/users/me/dataSources'

# Mapped Google Fit data sources
data_sources = {
    "steps": "derived:com.google.step_count.delta:com.google.android.gms:merge_step_deltas",
    "heart_rate": "derived:com.google.heart_rate.bpm:com.google.android.gms:merge_heart_rate_bpm",
    "calories": "derived:com.google.calories.expended:com.google.android.gms:merge_calories_expended"
}

# Fetch latest data from a given data source in the last 60 seconds
def fetch_latest_data(access_token, data_type, start_time, end_time):
    ds_id = data_sources.get(data_type)
    if not ds_id:
        return 0

    url = f"{BASE_URL}/{ds_id}/datasets/{start_time}000000-{end_time}000000"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {data_type}: {response.text}")
        return 0

    data = response.json()
    total = 0
    for point in data.get("point", []):
        for value in point.get("value", []):
            val = value.get("fpVal") or value.get("intVal")
            if isinstance(val, (int, float)):
                total += val
    return round(total)

# Unified data endpoint
def get_data(data_type):
    req = request.get_json()
    token = req.get('access_token')

    # Get current time and 1 minute ago
    now = int(time.time())
    one_min_ago = now - 60

    value = fetch_latest_data(token, data_type, one_min_ago, now)
    return jsonify({"value": value})

# Routes
@app.route('/api/steps', methods=['POST'])
def get_steps():
    return get_data("steps")

@app.route('/api/heart_rate', methods=['POST'])
def get_heart_rate():
    return get_data("heart_rate")

@app.route('/api/calories', methods=['POST'])
def get_calories():
    return get_data("calories")

# Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
