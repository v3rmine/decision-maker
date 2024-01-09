import uuid
from enum import Enum
from typing import List, Optional

from termcolor import colored

ENTITIES_NOT_ALLOWED = ['Memory', 'Ontology', 'Task', 'InterestPoint']
BASE_ENTITIES = ['Robot', 'Human', 'Object', 'Location']
ACCEPTED_TYPES = [bool, int, float, str]


class Languages(Enum):
    English = 'english'
    French = 'french'


class Middlewares(Enum):
    ROS2 = 'ROS2'
    API = 'API'


def entity_initialisation(self):
    for name, value in self.additional_attributes.items():
        self.__setattr__(name, value)


class InterestPoint:
    """
    Represent an interest point
    """
    id: int
    coordinates: (float, float)
    additional_attributes: dict = {}

    def __init__(self, id: int, coordinates: (float, float)):
        self.int = id
        self.coordinates = coordinates

        for name, value in self.additional_attributes.items():
            self.__setattr__(name, value)


class Location(object):
    """
    Represent a physical location
    """
    id: int
    name: str
    interest_points: List[InterestPoint]
    additional_attributes: dict = {}

    def __init__(self, id: int, name: str, interest_points: List[InterestPoint]):
        self.id = id
        self.name = name
        self.interest_points = interest_points

        for name, value in self.additional_attributes.items():
            self.__setattr__(name, value)


class Object(object):
    """
    Represent an object
    """
    id: str
    name: str
    category: Optional[str]
    interest_point: Optional[InterestPoint]
    additional_attributes: dict = {}

    def __init__(self, name: str, category: Optional[str] = None, interest_point: Optional[InterestPoint] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.category = category
        self.interest_point = interest_point

        for name, value in self.additional_attributes.items():
            self.__setattr__(name, value)


class Human(object):
    """
    Represent a human being
    """
    id: int
    name: str
    interest_point: InterestPoint
    additional_attributes: dict = {}

    def __init__(self, id: int, name: str, interest_point: InterestPoint):
        self.id = id
        self.name = name
        self.interest_point = interest_point

        for name, value in self.additional_attributes.items():
            self.__setattr__(name, value)


class Robot(object):
    """
    Represent a robot and its abilities
    """
    name: str
    middleware: Middlewares
    abilities: dict

    def __init__(self, name: str = 'Robot', middleware: Middlewares = Middlewares.ROS2, abilities: dict = {}):
        self.name = name
        self.middleware = middleware
        self.abilities = abilities


class Task:
    def __init__(self, name: str, prefix: str, params: dict, returns: type):
        self.name = name
        self.params = params
        self.returns = returns
        self.prefix = prefix


class Ontology:
    """
    Represent an ontology
    """

    def __init__(self, name: str = "default", description: str = "default description",
                 language: Languages = Languages.English):
        self.name = name
        self.description = description
        self.language = language
        self.available_tasks: List[Task] = []
        self.robot: Optional[Robot] = None
        self.entities: dict[str, type] = {
            'ROBOT': Robot,
            'HUMAN': Human,
            'OBJECT': Object,
            'LOCATION': Location
        }

    def print_entities(self, prefix=''):
        for entity in self.entities.values():
            attributes = ''

            for index, (attribute, value_type) in enumerate(entity.__annotations__.items()):
                if attribute.startswith('__'):
                    continue

                attributes += f'{attribute}: {colored(value_type.__name__, "light_red")}'

                if attribute in entity.__dict__:
                    if value_type == str:
                        attribute_str = '"' + entity.__dict__[attribute] + '"'
                        attributes += f' = {colored(attribute_str, "light_cyan")}'
                    else:
                        attributes += f' = {colored(entity.__dict__[attribute], "light_cyan")}'

                if index + 1 < len(entity.__annotations__):
                    attributes += ', '

            print(f'{prefix}{colored(entity.__name__, "light_magenta")}({attributes})')

    def print_tasks(self, prefix=''):
        for task in self.available_tasks:
            params = ''.join(
                [f'{param}: {colored(task.params[param].__name__, "light_yellow")}' for param in task.params])
            print(
                f'{prefix}{task.prefix}\\{colored(task.name, "light_magenta")}({params}) -> {colored(None if task.returns is None else task.returns.__name__, "light_red")}')


class Memory(dict):
    """
    Represent the robot memory
    """


ABILITIES = {
    'navigation_2d': [
        Task('get_current_interest_point', prefix='navigation_2d', params={}, returns=InterestPoint),
        Task('get_object_interest_point', prefix='navigation_2d', params={'object': Object}, returns=InterestPoint),
        Task('get_interest_point_location', prefix='navigation_2d', params={'interest_point': InterestPoint},
             returns=Location),
        Task('go_to', prefix='navigation_2d', params={'interest_point': InterestPoint}, returns=bool),
    ],
    'vision': [
        Task('detect_object', prefix='vision', params={'object': Object}, returns=Object),
        Task('detect_objects', prefix='vision', params={}, returns=List[Object]),
        Task('detect_humans', prefix='vision', params={}, returns=List[Object]),
    ],  # TODO: 'gesture_recognition'
    'object_grasping': [
        Task('grab_object', prefix='object_grasping', params={'object': Object}, returns=bool),
        Task('put_object', prefix='object_grasping', params={'object': Object}, returns=bool),
    ],  # TODO: 'push_object', 'pull_object'
    'speech_recognition': [
        Task('speech_to_text', prefix='speech_recognition', params={}, returns=str),
        Task('detect_sound', prefix='speech_recognition', params={}, returns=bool),
    ],  # TODO: 'detect_language'
    'text_to_speech': [
        Task('say', prefix='text_to_speech', params={'text': str}, returns=None),
    ],  # TODO: 'change_language'
    'display': [
        Task('display_text', prefix='display', params={'text': str}, returns=None),
    ],  # TODO: 'display_image', 'display_video'
    'audio': [
        Task('play_sound', prefix='audio', params={'sound_name': str}, returns=None),
    ]
}
