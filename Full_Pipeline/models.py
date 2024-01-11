import builtins
import typing
import uuid
from enum import Enum
from typing import List, Optional

from termcolor import colored

from middlewares import Middlewares
from pipeline import TaskList

ENTITIES_NOT_ALLOWED = ['Memory', 'Ontology', 'Task', 'InterestPoint']
BASE_ENTITIES = ['Robot', 'Human', 'Object', 'Location']
ACCEPTED_TYPES = [bool, int, float, str]


class Languages(Enum):
    English = 'english'
    French = 'french'


def entity_initialisation(self):
    """
        Add the values in additional_attributes as real class attributes

        :param self:
    """
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

        entity_initialisation(self)


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

        entity_initialisation(self)


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

        entity_initialisation(self)


class Human(object):
    """
    Represent a human being
    """

    id: str
    name: str
    interest_point: Optional[InterestPoint]
    is_querier: bool
    additional_attributes: dict = {}

    def __init__(self, name: str, interest_point: Optional[InterestPoint] = None, is_querier = False):
        self.id = str(uuid.uuid4())
        self.name = name
        self.interest_point = interest_point
        self.is_querier = is_querier

        entity_initialisation(self)


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


class Ontology:
    """
    Represent an ontology
    """

    def __init__(self, name: str = "default", description: str = "default description", language: Languages = Languages.English):
        self.name = name
        self.description = description
        self.language = language
        self.available_tasks = TaskList([])
        self.robot: Optional[Robot] = None
        self.entities: dict[str, type] = {
            'ROBOT': Robot,
            'HUMAN': Human,
            'OBJECT': Object,
            'LOCATION': Location
        }
        self.NER_labels = list(self.entities.keys())
        self.REL_relations = []

    def print_entities(self, prefix=''):
        """
            Print the ontology entities

            :param prefix:
        """

        for entity in self.entities.values():
            attributes = ''

            for index, (attribute, value_type) in enumerate(entity.__annotations__.items()):
                if attribute.startswith('__'):
                    continue
                elif attribute == 'additional_attributes':
                    continue

                attributes += print_attribute(attribute, value_type, entity.__dict__)

                if index + 1 < len(entity.__annotations__):
                    attributes += ', '

            if hasattr(entity, 'additional_attributes'):
                for (attribute, value) in entity.additional_attributes.items():
                    attributes += print_attribute(attribute, type(value), entity.additional_attributes)

            print(f'{prefix}{colored(entity.__name__, "light_magenta")}({attributes})')

    def print_tasks(self, prefix=''):
        """
            Print the ontology tasks

            :param prefix:
        """

        for task in self.available_tasks:
            params = ''.join([f'{param}: {colored(task.params[param].__name__, "light_yellow")}' for param in task.params])
            print(f'{prefix}{task.category}\\{colored(task.name, "light_magenta")}({params}) -> {colored(None if task.returns is None else task.returns.__name__, "light_red")}')


def print_attribute(attribute: str, value_type: type, attributes) -> str:
    """
        Print an attribute

        :param attribute:
        :param value_type:
        :param attributes:
    """

    result = f'{attribute}: '

    match typing.get_origin(value_type):
        case typing.Union:
            type_str = f'{value_type.__qualname__}[{value_type.__args__[0].__name__}]'
            result += f'{colored(type_str, "light_red")}'

        case _:
            result += f'{colored(value_type.__name__, "light_red")}'

    if attribute in attributes:
        match value_type:
            case builtins.str:
                attribute_str = '"' + attributes[attribute] + '"'
                result += f' = {colored(attribute_str, "light_cyan")}'
            case _:
                result += f' = {colored(attributes[attribute], "light_cyan")}'

    return result
