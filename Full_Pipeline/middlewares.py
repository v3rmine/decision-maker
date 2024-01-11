import time
from enum import Enum

import jsonpickle
import requests


class Middlewares(Enum):
    ROS2 = 'ROS2'
    API = 'API'


def send_api_action(url: str, params: dict):
    print(f'Sending data to API URL {url}...')

    response = requests.post(
        url,
        json=jsonpickle.encode(params)
    )

    json_response = response.content
    print('Response:', str(json_response))

    return jsonpickle.decode(json_response)


def send_ros_action(topic_name: str, params: dict):
    print(f'Sending to ROS Topic {topic_name}...')
    time.sleep(2)
    print('Sent')
