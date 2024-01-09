import json

from flask import Flask, request, jsonify

app = Flask(__name__)

API_PREFIX = '/api'


@app.post(f'{API_PREFIX}/vision/detect_object', endpoint='detect_object')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    print(data['object'])

    return data['object']


@app.post(f'{API_PREFIX}/object_grasping/grab_object', endpoint='grab_object')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    print(data['object'])

    return jsonify(True)
