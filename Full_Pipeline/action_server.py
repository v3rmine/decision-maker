import jsonpickle

import models
import json

from flask import Flask, request, jsonify

app = Flask(__name__)

API_PREFIX = '/api'


def create_interest_point(coordinates: (float, float)):
    interest_point_class = eval('models.InterestPoint')
    interest_point = interest_point_class(coordinates)
    json_interest_point = jsonpickle.encode(interest_point)
    return json.loads(json_interest_point)


@app.post(f'{API_PREFIX}/vision/detect_object', endpoint='detect_object')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    data['object']['interest_point'] = create_interest_point((3.0, 3.0))

    print(data['object'])

    return data['object']


@app.post(f'{API_PREFIX}/vision/detect_human', endpoint='detect_human')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    data['human']['interest_point'] = create_interest_point((1.0, 2.0))

    print(data['human'])

    return data['human']


@app.post(f'{API_PREFIX}/object_grasping/grab_object', endpoint='grab_object')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    print(data['object'])

    return jsonify(True)


@app.post(f'{API_PREFIX}/navigation_2d/go_to_location', endpoint='go_to_location')
def go_to_location():
    content = request.get_json()
    data = json.loads(content)

    print(data['location'])

    return jsonify(True)


@app.post(f'{API_PREFIX}/navigation_2d/go_to_interest_point', endpoint='go_to_interest_point')
def go_to_interest_point():
    content = request.get_json()
    data = json.loads(content)

    print(data['interest_point'])

    return jsonify(True)
