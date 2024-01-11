import builtins
import collections
import re
from collections import defaultdict

from spacy.tokens import Span
from spacy_llm.tasks.rel import RelationItem
from termcolor import colored

import models
import pipeline
from constants import GOALS
from llm import EntityRelation
from middlewares import Middlewares, send_ros_action, send_api_action
from models import Ontology
from pipeline import Goal, RetrieveProperty, Condition, Task


class MemoryStack(defaultdict[str, collections.deque]):
    def __init__(self):
        super(MemoryStack, self).__init__(collections.deque)


class Memory:
    def __init__(self):
        self.ontology: Ontology = None
        self.entities: list[Span] = []
        self.relations: list[EntityRelation] = []
        self.goals: list[Goal] = []
        self.memory_stack = MemoryStack()
        self.answers: list[dict] = []

    def print_entities(self):
        for entity in self.entities:
            print('\t', colored(entity.label_, attrs=['bold']), entity)
        print()

    def print_memory_stack(self):
        for entity_name in self.memory_stack:
            print('\t', entity_name)
            for entity in self.memory_stack[entity_name]:
                print('\t\t-', end='')

                for key, value in vars(entity).items():
                    print(f' {key}={value}', end='')

                print()

    def assemble_entity(self, entity: Span):
        entity_class: type = self.ontology.entities[entity.label_]

        match entity_class:
            case models.Object:
                assembled_entity = entity_class(entity.text)

            case models.Human:
                if entity.text.lower() in ['me', 'my', 'myself', 'i']:
                    is_querier = True
                else:
                    is_querier = False

                assembled_entity = entity_class(entity.text, is_querier=is_querier)

            case models.Robot:
                assembled_entity = self.ontology.robot

            case _:
                assembled_entity = entity_class()

        for relation in self.relations:
            if relation.dependency == entity:
                attribute = relation.destination
                assembled_entity.__setattr__(attribute.label_.lower(), attribute.text)

        return assembled_entity

    def select_relations(self, candidate_relations: list[RelationItem]):
        entities_to_remove: list[int] = []

        for relation in candidate_relations:
            relation_entities = re.match(r'^(\w+)Has(\w+)$', relation.relation).groups()

            relation_dest_class_label = relation_entities[1].upper()
            relation_dep_class_label = relation_entities[0].upper()

            dest_entity_class = self.entities[relation.dest]
            dep_entity_class = self.entities[relation.dep]

            if dest_entity_class.label_ == relation_dest_class_label and dep_entity_class.label_ == relation_dep_class_label:
                print(f'\tACCEPTED {relation.relation} dest={relation.dest}, dep={relation.dep}')
                self.relations.append(EntityRelation(dest_entity_class, dep_entity_class, relation.relation))
                entities_to_remove.append(relation.dest)
            else:
                print(colored(f'\tREJECTED {relation.relation} dest={relation.dest}, dep={relation.dep}', 'grey'))

        for entity_to_remove in entities_to_remove:
            del self.entities[entity_to_remove]

    def select_goals(self, candidate_goals: dict[str, float]):
        for key, score in candidate_goals.items():
            if score == 1.0:
                print(f'\t{key} {score}')

                goal = GOALS[key]

                # Find goal from TextCat
                self.goals.append(goal)

            else:
                print(colored(f'\t{key} {score}', 'grey'))

    def fill_answers_and_memory_stack(self):
        for goal in self.goals:
            print('\t', goal.name)

            params_entities_name = []

            for entity in self.entities:
                if entity.label_.upper() not in self.ontology.entities:
                    continue

                # Recompose entity
                new_entity = self.assemble_entity(entity)

                # Add entity to the memory stack
                self.memory_stack[entity.label_].append(new_entity)

            for param in goal.params:
                if param not in self.memory_stack:
                    print(f'Missing parameter {param}')
                    exit(0)
                else:
                    params_entities_name.append(self.memory_stack[param][0].name)

            self.answers.append({
                'validation': goal.validation(*params_entities_name),
                'answer': goal.answer(*params_entities_name),
            })

            for pipeline_element in goal.pipeline:
                match type(pipeline_element):
                    case pipeline.Task:
                        print('\t\t-', pipeline_element.name, pipeline_element.params, '->', pipeline_element.returns)

                    case pipeline.Condition:
                        print('\t\t- Condition', pipeline_element.condition_value)

                    case pipeline.RetrieveProperty:
                        print('\t\t- Retrieve', pipeline_element.input_type, '->', pipeline_element.output_type)

    def execute_pipeline(self):
        for goal_index, current_goal in enumerate(self.goals):
            print(colored(f'\tGoal {goal_index + 1} - {current_goal.name}', attrs=['bold']))

            print('\t>', self.answers[goal_index]['validation'], '\n')

            for pipeline_element_index, current_pipeline_element in enumerate(current_goal.pipeline):
                match type(current_pipeline_element):
                    case pipeline.RetrieveProperty:
                        self.handle_retrieve_property(index=pipeline_element_index, retrieve_property=current_pipeline_element)

                    case pipeline.Condition:
                        self.handle_condition(index=pipeline_element_index, condition=current_pipeline_element)

                    case pipeline.Task:
                        self.handle_task(index=pipeline_element_index, task=current_pipeline_element)

            print('\t>', self.answers[goal_index]['answer'])
            print()

    def handle_retrieve_property(self, index: int, retrieve_property: RetrieveProperty):
        print(colored(f'\t\tTask {index + 1} - Retrieving {retrieve_property.output_type} from {retrieve_property.input_type}', attrs=['bold']))

        input_type = retrieve_property.input_type.__name__.upper()
        output_type = retrieve_property.output_type.__name__.upper()

        input_value = self.memory_stack[input_type].pop()
        output_value = retrieve_property.fit(input_value)

        self.memory_stack[output_type].append(output_value)

    def handle_condition(self, index: int, condition: Condition):
        print(colored(f'\t\tTask {index + 1} - Condition {condition.condition_value}', attrs=['bold']))

    def handle_task(self, index: int, task: Task):
        print(colored(f'\t\tTask {index + 1} - {task.name}', attrs=['bold']))

        completed_params = {}

        for param, value in task.params.items():
            entity_reference = value.__name__.upper()
            completed_params[param] = self.memory_stack[entity_reference].pop()

        print('\t\t\t> Params:', completed_params, '\n')

        match self.ontology.robot.middleware:
            # ROS 2
            case Middlewares.ROS2:
                topic_name = f'{task.category}/{task.name}'
                response = send_ros_action(topic_name, completed_params)

            # API
            case Middlewares.API:
                url = f'http://127.0.0.1:5000/api/{task.category}/{task.name}'
                response = send_api_action(url, completed_params)

        print('\n\t\t\t> Returned:', response, '\n')

        match task.returns:
            case None:
                pass

            case builtins.bool:
                if not response:
                    print('ALED')

            case _:
                return_type_name = task.returns.__name__.upper()
                self.memory_stack[return_type_name].append(response)