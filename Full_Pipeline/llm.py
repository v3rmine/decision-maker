from spacy.tokens import Span
from typing_extensions import List

LLM_MODEL = {
    'model': {
        '@llm_models': 'spacy.GPT-4.v2',
        'name': 'gpt-4',
        'config': {'temperature': 0.0}
    }
}


def generate_ner_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.NER.v2',
            'labels': labels,  # ['ROBOT', 'HUMAN', 'LOCATION', 'OBJECT', 'FURNITURE', 'COLOR', 'AGE', 'WEIGHT']
            'label_definitions': {
                'ROBOT': 'You as a general purpose service robot, e.g. you, your',
                'HUMAN': 'A person, e.g. I, me, him, John, her, Anna.',
                'LOCATION': 'A room in a house, e.g. kitchen, living-room, bathroom',
                'OBJECT': 'Any object that can be used by a human, e.g. pencil, apple, drink, phone',
                # Any object that can be found in a house
            },
        },
        **LLM_MODEL
    }


def generate_rel_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.REL.v1',
            'labels': labels,
        },
        **LLM_MODEL
    }


def generate_textcat_config(labels: List[str]):
    return {
        'task': {
            '@llm_tasks': 'spacy.TextCat.v3',
            'labels': labels
        },
        **LLM_MODEL
    }


class EntityRelation:
    """
        Similar to SpaCy RelationItem but stores the whole entities instead of their doc index
    """

    def __init__(self, destination: Span, dependency: Span, name: str):
        self.destination = destination
        self.dependency = dependency
        self.name = name
