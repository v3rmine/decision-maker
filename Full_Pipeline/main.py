import collections
import json
import re
from collections import defaultdict

import jsonpickle
import spacy
from spacy.tokens.span import Span
from spacy_llm.tasks.rel import RelationItem
from termcolor import colored
from typing_extensions import List, Sequence

from middlewares import send_ros_action, send_api_action
from models import Ontology, Object, Task, Middlewares, Location, Robot
from parse_ontology import parseOntologyConfig


class EntityRelation:
    def __init__(self, dest: Span, dep: Span, name: str):
        self.dest = dest
        self.dep = dep
        self.name = name


class Goal:
    def __init__(self, name: str, params: List[str], pipeline: List[str], validation: callable, answer: callable):
        self.name = name
        self.params = params
        self.pipeline = pipeline
        self.validation = validation
        self.answer = answer


# TODO generate this with ontology
GOALS = [
    Goal(
        'GRAB AN OBJECT',
        params=['OBJECT'],
        pipeline=[
            'detect_object',
            'grab_object',
        ],
        validation=lambda object: f'I am going to grab a {object}.',
        answer=lambda object: f'I am done grabbing {object}.',
    ),
    Goal(
        'GRAB AN OBJECT IN A LOCATION',
        params=['OBJECT', 'LOCATION'],
        pipeline=[
            'go_to'
            'detect_object',
            'grab_object',
        ],
        validation=lambda object, location: f'I am going to grab a {object} in the {location}.',
        answer=lambda object, location: f'I am done grabbing {object} in {location}.',
    ),
    Goal(
        'BRING AN OBJECT TO SOMEONE',
        params=[],
        pipeline=[
        ],
        validation=lambda _: f'',
        answer=lambda _: f'',
    ),
    Goal(
        'BRING AN OBJECT IN A LOCATION TO SOMEONE',
        params=[],
        pipeline=[
        ],
        validation=lambda _: f'',
        answer=lambda _: f'',
    ),
    Goal(
        'SAY SOMETHING',
        params=[],
        pipeline=[
        ],
        validation=lambda _: f'',
        answer=lambda _: f'',
    ),
    Goal(
        'GO TO LOCATION',
        params=[],
        pipeline=[
        ],
        validation=lambda _: f'',
        answer=lambda _: f'',
    ),
]

# TODO: generate this with ontology
NER_CONFIG = {
    'task': {
        '@llm_tasks': 'spacy.NER.v2',
        'labels': ['ROBOT', 'HUMAN', 'LOCATION', 'OBJECT', 'COLOR', 'AGE', 'WEIGHT'],
        'label_definitions': {
            'ROBOT': 'You as a general purpose service robot, e.g. you, your',
            'PERSON': 'A person, e.g. I, me, him, John, her, Anna.',
            'LOCATION': 'A room in a house, e.g. kitchen, living-room, bathroom',
            'OBJECT': 'Any object that can be found in a house, e.g. pencil, apple, drink, phone',
        },
    },
    'model': {
        '@llm_models': 'spacy.GPT-3-5.v2',
        'name': 'gpt-3.5-turbo',
        'config': {'temperature': 0.0}
    }
}

REL_CONFIG = {
    'task': {
        '@llm_tasks': 'spacy.REL.v1',
        'labels': ['ObjectHasColor', 'PersonHasAge', 'ObjectHasWeight'],
    },
    'model': {
        '@llm_models': 'spacy.GPT-3-5.v2',
        'name': 'gpt-3.5-turbo',
        'config': {'temperature': 0.0}
    }
}

TEXTCAT_CONFIG = {
    'task': {
        '@llm_tasks': 'spacy.TextCat.v3',
        'labels': [goal.name for goal in GOALS]
    },
    'model': {
        '@llm_models': 'spacy.GPT-3-5.v2',
        'name': 'gpt-3.5-turbo',
        'config': {'temperature': 0.0}
    }
}


def print_memory_stack(stack: defaultdict[str, collections.deque]):
    for entity_name in stack:
        print('\t', entity_name)
        for entity in task_memory_stack[entity_name]:
            print('\t\t-', entity.name)


def assemble_entity(entity: Span, ontology: Ontology, entities: Sequence[Span], relations: List[EntityRelation]):
    entity_class: type = ontology.entities[entity.label_]

    if entity_class == Object:
        assembled_entity = entity_class(entity.text_with_ws)
    elif entity_class == Robot:
        assembled_entity = ontology.robot
    else:
        assembled_entity = entity_class()

    for relation in relations:
        if relation.dep == entity:
            attribute = relation.dest
            assembled_entity.__setattr__(attribute.label_.lower(), attribute.text)

    return assembled_entity


if __name__ == '__main__':
    """
    
        ONTOLOGY
    
    """

    ontology = parseOntologyConfig('ontology_v2.toml')

    print()

    """
    
        SPACY
    
    """

    spacy.prefer_gpu()

    print('Loading model...')
    nlp = spacy.load('en_core_web_lg')  # en_core_web_lg
    print('Model loaded!')

    # Named Entity Recognition
    ner_llm = nlp.add_pipe('llm_ner', config=NER_CONFIG)

    # Relation extraction
    rel_llm = nlp.add_pipe('llm_rel', config=REL_CONFIG)

    # Text Categorizer
    textcat_llm = nlp.add_pipe('llm_textcat', config=TEXTCAT_CONFIG)

    # Rule-based sentence splitting on punctuation e.g. . ! ?
    nlp.add_pipe('sentencizer')

    try:
        while True:
            print('------------------------')
            input_text = input('Enter a sentence: ')
            print()

            # Process text
            doc = nlp(input_text)

            # === ENTITIES ===

            print(colored('ENTITIES', attrs=['underline']))

            entities = list(doc.ents)
            for entity in entities:
                print('\t', colored(entity.label_, attrs=['bold']), entity)
            print()

            # === RELATIONS ===

            print(colored('RELATIONS', attrs=['underline']))

            relations: List[RelationItem] = doc._.rel
            validated_relations: List[EntityRelation] = []

            for relation in relations:
                relation_entities = re.match(r'^(\w+)Has(\w+)$', relation.relation).groups()

                relation_dest_class_label = relation_entities[1].upper()
                relation_dep_class_label = relation_entities[0].upper()

                dest_entity_class = entities[relation.dest]
                dep_entity_class = entities[relation.dep]

                if dest_entity_class.label_ == relation_dest_class_label and dep_entity_class.label_ == relation_dep_class_label:
                    validated_relations.append(EntityRelation(dest_entity_class, dep_entity_class, relation.relation))
                    # TODO: Not sure
                    entities.remove(dest_entity_class)
                    print(f'\tACCEPTED {relation.relation} dest={relation.dest}, dep={relation.dep}')
                else:
                    print(colored(f'\tREJECTED {relation.relation} dest={relation.dest}, dep={relation.dep}', 'grey'))

            print()

            # === GOAL ===

            print(colored('GOALS', attrs=['underline']))

            validated_goals: List[Goal] = []

            for key, score in doc.cats.items():
                if score == 1.0:
                    print(f'\t{key} {score}')

                    # Find goal from TextCat
                    for goal in GOALS:
                        if key == goal.name:
                            validated_goals.append(goal)

                else:
                    print(colored(f'\t{key} {score}', 'grey'))

            # === NLP ===

            print(colored('\nWORDS', attrs=['underline']))

            for token in doc:
                print('\t', colored(token.text, attrs=['bold']), '\t|', token.dep_, token.pos_,
                      token.ent_type_ if token.ent_type_ != '' else '∅',
                      token.head.text, [child for child in token.children])

            # === FILL TASK MEMORY STACK AND TASK LIST ===

            print(colored('\nTASKS', attrs=['underline']))

            task_list: List[Task] = []
            task_memory_stack: defaultdict[str, collections.deque] = defaultdict(collections.deque)
            answers: List[str] = []

            for goal in validated_goals:
                print('\t', goal.name)

                params_entities_name = []

                for entity in entities:
                    # Recompose entity
                    new_entity = assemble_entity(entity, ontology, entities, validated_relations)

                    # Add entity to the memory stack
                    task_memory_stack[entity.label_].append(new_entity)

                for param in goal.params:
                    if param not in task_memory_stack:
                        answers.append(f'Missing parameter {param}')
                        continue
                    else:
                        params_entities_name.append(task_memory_stack[param][0].name)

                answer = goal.validation(*params_entities_name)
                answers.append(answer)

                for task in goal.pipeline:
                    for available_task in ontology.available_tasks:
                        if available_task.name == task:
                            task_list.append(available_task)
                            print('\t\t-', available_task.name, available_task.params, '->', available_task.returns)

            print(colored('\nMEMORY STACK', attrs=['underline']))

            print_memory_stack(task_memory_stack)

            print()

            # === EXECUTE TASK PIPELINE ===

            print(colored('TASK PIPELINE', attrs=['underline']))

            for index, current_task in enumerate(task_list):
                print(f'\tTask {index + 1} - {current_task.name}\n')

                completed_params = {}
                return_type_name = current_task.returns.__name__.upper()

                for param in current_task.params:
                    entity_reference = current_task.params[param].__name__.upper()
                    completed_params[param] = task_memory_stack[entity_reference].pop()

                # ROS 2
                if ontology.robot.middleware == Middlewares.ROS2:
                    topic_name = f'{current_task.prefix}/{current_task.name}'
                    response = send_ros_action(topic_name, completed_params)
                # API
                elif ontology.robot.middleware == Middlewares.API:
                    url = f'http://127.0.0.1:5000/api/{current_task.prefix}/{current_task.name}'
                    response = send_api_action(url, completed_params)

                task_memory_stack[return_type_name].append(response)

                print()

    except KeyboardInterrupt:
        exit(0)
