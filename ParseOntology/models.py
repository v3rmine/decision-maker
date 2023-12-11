from enum import Enum
from typing import List

ENTITIES_NOT_ALLOWED = ['Memory', 'Ontology', 'Task', 'InterestPoint']
BASE_ENTITIES = ['Robot', 'Human', 'Object', 'Location']
ACCEPTED_TYPES = [bool, int, float, str]

class Languages(Enum):
    English = 'english'
    French = 'french'

class Middlewares(Enum):
    ROS2 = 'ROS2'

class InterestPoint:
    """
    Represent an interest point
    """
    id: int
    coordinates: (float, float)

    def __init__(self, id: int, coordinates: (float, float)):
        self.int = id
        self.coordinates = coordinates

class Location:
    """
    Represent a physical location
    """
    id: int
    name: str
    interest_points: List[InterestPoint]

    def __init__(self, id: int, name: str, interest_points: List[InterestPoint]):
        self.id = id
        self.name = name
        self.interest_points = interest_points

class Object:
    """
    Represent an object
    """
    id: int
    name: str
    category: str
    interest_point: InterestPoint

    def __init__(self, id: int, name: str, category: str, interest_point: InterestPoint):
        self.id = id
        self.name = name
        self.category = category
        self.interest_point = interest_point

class Human:
    """
    Represent a human being
    """
    id: int
    name: str
    interest_point: InterestPoint

    def __init__(self, id: int, name: str, interest_point: InterestPoint):
        self.id = id
        self.name = name
        self.interest_point = interest_point

class Robot:
    """
    Represent a robot and its abilities
    """
    name: str
    middleware: str
    abilities: dict

    def __init__(self, name: str = 'Robot', middleware: str = 'ROS2', abilities: dict = {}):
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
    def __init__(self, name: str = "default", description: str = "default description", language: Languages = Languages.English):
        self.name = name
        self.description = description
        self.language = language
        self.available_tasks: List[Task] = []
        self.entities: dict[str, type] = {}

    def print_entities(self, prefix = ''):
        for entity in self.entities.values():
            attributes = ''

            for index, (attribute, value_type) in enumerate(entity.__annotations__.items()):
                if attribute.startswith('__'):
                    continue

                attributes += f'{attribute}: {value_type.__qualname__}'

                if attribute in entity.__dict__:
                    if value_type == str:
                        attributes += f' = "{entity.__dict__[attribute]}"'
                    else:
                        attributes += f' = {entity.__dict__[attribute]}'

                if index + 1 < len(entity.__annotations__):
                    attributes += ', '

            print(f'{prefix}{entity.__qualname__}({attributes})')

    def print_tasks(self, prefix = ''):
        for task in self.available_tasks:
            params = ''.join([f'{param}: {task.params[param].__qualname__}' for param in task.params])
            print(f'{prefix}{task.prefix}\\{task.name}({params}) -> {None if task.returns is None else task.returns.__qualname__}')

class Memory(dict):
    """
    Represent the robot memory
    """


def ability_to_task_list(ability: str) -> List[Task]:
    """
    Return a list of task linked to an ability

    :param ability:
    :return:
    """
    tasks = []
    for task_dict in ABILITIES[ability]:
        task = Task(task_dict, ABILITIES[ability][task_dict]['params'], ABILITIES[ability][task_dict]['returns'])
        tasks.append(task)

    return tasks

ABILITIES = {
    'navigation_2d': {
        'get_current_interest_point': {
            'params': {},
            'returns': InterestPoint
        },
        'get_object_interest_point': {
            'params': { 'object': Object },
            'returns': InterestPoint
        },
        'get_interest_point_location': {
            'params': { 'interest_point': InterestPoint },
            'returns': Location
        },
        'go_to': {
            'params': { 'interest_point': InterestPoint },
            'returns': bool
        },
    },
    'vision': {
        'detect_objects': {
            'params': {},
            'returns': List[Object]
        },
        'detect_humans': {
            'params': {},
            'returns': List[Human]
        },
    }, # TODO: 'gesture_recognition'
    'object_grasping': {
        'grab_object': {
            'params': { 'object': Object },
            'returns': bool
        },
        'put_object': {
            'params': { 'object': Object },
            'returns': bool
        },
    }, # TODO: 'push_object', 'pull_object'
    'speech_recognition': {
        'speech_to_text': {
            'params': {},
            'returns': str
        },
        'detect_sound': {
            'params': {},
            'returns': bool
        }, # 'detect_language'
    },
    'text_to_speech': {
        'say': {
            'params': { 'text': str },
            'returns': None
        }
    }, # TODO: 'change_language'
    'display': {
        'display_text': {
            'params': { 'text': str },
            'returns': None
        }
    }, # TODO: 'display_image', 'display_video'
    'audio': {
        'play_sound': {
            'params': { 'sound_name': str },
            'returns': None
        }
    }
}