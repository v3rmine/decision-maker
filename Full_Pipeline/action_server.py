import random
import time
import jsonpickle
import json
import pyttsx3
import models

from flask import Flask, request, jsonify, Response

app = Flask(__name__)

API_PREFIX = '/api'


def random_wait():
    time.sleep(random.random() * 4 + 1)


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

    random_wait()

    return data['object']


@app.post(f'{API_PREFIX}/vision/detect_human', endpoint='detect_human')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    data['human']['interest_point'] = create_interest_point((1.0, 2.0))

    print(data['human'])

    random_wait()

    return data['human']


@app.post(f'{API_PREFIX}/object_grasping/grab_object', endpoint='grab_object')
def detect_object():
    content = request.get_json()
    data = json.loads(content)

    print(data['object'])

    random_wait()

    return jsonify(True)


@app.post(f'{API_PREFIX}/navigation_2d/go_to_location', endpoint='go_to_location')
def go_to_location():
    content = request.get_json()
    data = json.loads(content)

    print(data['location'])

    random_wait()

    return jsonify(True)


@app.post(f'{API_PREFIX}/navigation_2d/go_to_interest_point', endpoint='go_to_interest_point')
def go_to_interest_point():
    content = request.get_json()
    data = json.loads(content)

    print(data['interest_point'])

    random_wait()

    return jsonify(True)


@app.post(f'{API_PREFIX}/text_to_speech/say', endpoint='say')
def say():
    content = request.get_json()
    data = json.loads(content)

    print(data['text'])

    engine = pyttsx3.init()
    engine.setProperty('rate', 135)
    engine.say(data['text'])
    engine.runAndWait()

    return Response(status=204)
