from spacy.tokens import Span
from typing_extensions import List


def generate_ner_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.NER.v2',
            'labels': labels,  # ['ROBOT', 'HUMAN', 'LOCATION', 'OBJECT', 'FURNITURE', 'COLOR', 'AGE', 'WEIGHT']
            'label_definitions': {
                'ROBOT': 'You as a general purpose service robot, e.g. you, your',
                'PERSON': 'A person, e.g. I, me, him, John, her, Anna.',
                'LOCATION': 'A room in a house, e.g. kitchen, living-room, bathroom',
                'OBJECT': 'Any object that can be used by a human, e.g. pencil, apple, drink, phone',
                # Any object that can be found in a house
            },
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v2',
            'name': 'gpt-3.5-turbo',
            'config': {'temperature': 0.0}
        }
    }


def generate_rel_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.REL.v1',
            'labels': labels,
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v2',
            'name': 'gpt-3.5-turbo',
            'config': {'temperature': 0.0}
        }
    }


def generate_textcat_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.TextCat.v3',
            'labels': labels
        },
        'model': {
            '@llm_models': 'spacy.GPT-3-5.v2',
            'name': 'gpt-3.5-turbo',
            'config': {'temperature': 0.0}
        }
    }


class EntityRelation:
    def __init__(self, destination: Span, dependency: Span, name: str):
        self.destination = destination
        self.dependency = dependency
        self.name = name
