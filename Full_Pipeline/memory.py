import builtins
import collections
import re
from collections import defaultdict

from spacy.tokens import Span
from spacy_llm.tasks.rel import RelationItem
from termcolor import colored

import models
import pipeline
from constants import BASE_GOALS
from llm import EntityRelation
from middlewares import Middlewares, send_ros_action, send_api_action
from models import Ontology
from pipeline import Goal, RetrieveProperty, Condition, Task


class MemoryStack(defaultdict[str, collections.deque]):
    def __init__(self):
        super(MemoryStack, self).__init__(collections.deque)


class GoalAnswer:
    """
        Computed version of Goal "validation" and "finished" callable properties
    """

    validation: str
    """
        Goal validation sentence. e.g. I am going to bring you a cup of tea
    """

    finished: str
    """
        Finished goal sentence. e.g. I am done bringing you a cup of tea
    """

    def __init__(self, validation: str, finished: str):
        self.validation = validation
        self.finished = finished


class Memory:
    ontology: Ontology
    """
        Data parsed from the ontology TOML file where is specified what are the robot abilities and understanding depth
    """

    entities: list[Span]
    """
        List of entities tagged from the NLP. e.g. HUMAN, OBJECT, LOCATION 
    """

    relations: list[EntityRelation]
    """
        List of relations between two entities
    """

    goals: list[Goal]
    """
        List of goals that can be executed by the robot
    """

    memory_stack: MemoryStack
    """
        Short-term memory that contains a FIFO queue for each registered entity
    """

    answers: list[GoalAnswer]
    """
        List of computed answers originating from Goal "validation" and "finished" callable properties
    """

    def __init__(self, ontology: Ontology):
        self.ontology = ontology
        self.entities: list[Span] = []
        self.relations: list[EntityRelation] = []
        self.goals: list[Goal] = []
        self.memory_stack = MemoryStack()
        self.answers: list[GoalAnswer] = []

    def reset(self):
        """
            Reset the memory
        """
        self.entities: list[Span] = []
        self.relations: list[EntityRelation] = []
        self.goals: list[Goal] = []
        self.answers: list[GoalAnswer] = []

    def print_entities(self):
        """
            Pretty print the memory entities
        """

        for entity in self.entities:
            print('\t', colored(entity.label_, attrs=['bold']), entity)
        print()

    def print_memory_stack(self):
        """
            Pretty print the memory stack
        """

        for entity_name in self.memory_stack:
            print('\t', entity_name)
            for entity in self.memory_stack[entity_name]:
                print('\t\t-', end='')

                for key, value in vars(entity).items():
                    print(f' {key}={value}', end='')

                print()

    def assemble_entity(self, entity: Span):
        """
            Assemble a given NLP entity into a real python object

            :param entity:
        """

        entity_label = entity.label_
        entity_text = entity.text

        # Get the ontology class from which the entity belongs
        entity_class: type = self.ontology.entities[entity_label]

        # Match different assembly possibilities
        match entity_class:
            # Object
            case models.Object:
                # assemble the entity to the Object class
                assembled_entity: models.Object = entity_class(entity_text)

            # Human
            case models.Human:
                # Check if the human is the querier of the sentence
                if entity_text.lower() in ['me', 'my', 'myself', 'i']:
                    is_querier = True
                else:
                    is_querier = False

                # assemble the entity to the Human class
                assembled_entity: models.Human = entity_class(entity_text, is_querier=is_querier)

            # Robot
            case models.Robot:
                # assemble the entity to the Robot class
                assembled_entity: models.Robot = self.ontology.robot

            # Location
            case models.Location:
                # assemble the entity to the Location class
                assembled_entity: models.Location = entity_class(entity_text)

            case _:
                # assemble the entity to another class, likely the entities registered from the ontology
                assembled_entity = entity_class()

        # For each validated relation
        for relation in self.relations:
            # If the relation is pointing to our entity
            if relation.dependency == entity:
                # Get the attribute
                attribute = relation.destination

                # Affect the attribute to our entity
                assembled_entity.__setattr__(attribute.label_.lower(), attribute.text)

        return assembled_entity

    def select_relations(self, candidate_relations: list[RelationItem]):
        """
            Select the relations that are valid based on their conformity

            :param candidate_relations:
        """

        # Array of entities to remove from the entity list. Because they are an attribute of a real entity and not an entity themselves.
        # e.g. ObjectHasColor -> Color has to be removed from the entity list because it's only an attribute of Object
        entities_to_remove: list[int] = []

        # For each candidate relation
        for relation in candidate_relations:
            relation_name = relation.relation

            # Use a Regex to extract the two parts of the relation
            relation_classes = re.match(r'^(\w+)Has(\w+)$', relation_name).groups()

            # e.g. ObjectHasColor
            # destination: Color
            dest_class_label = relation_classes[1].upper()
            # dependency: Object
            dep_class_label = relation_classes[0].upper()

            # Get the destination entity
            dest_entity_class = self.entities[relation.dest]
            # Get the dependency entity
            dep_entity_class = self.entities[relation.dep]

            # Ensure that the class of the retrieved entities are the same as the one written in the relation name
            # e.g. that in the ObjectHasColor relation, dependency is Object and destination is Color
            if dest_entity_class.label_ == dest_class_label and dep_entity_class.label_ == dep_class_label:
                print(f'\tACCEPTED {relation_name} dest={relation.dest}, dep={relation.dep}')

                # Add the relation to the memory with the entities saved so that the destination can be removed from the entities
                self.relations.append(EntityRelation(dest_entity_class, dep_entity_class, relation_name))

                # Add the index of the destination entity in order to remove it further
                entities_to_remove.append(relation.dest)
            else:
                print(colored(f'\tREJECTED {relation_name} dest={relation.dest}, dep={relation.dep}', 'grey'))

        # For each entity to remove
        for entity_to_remove in entities_to_remove:
            # Remove the entity from the entity list
            del self.entities[entity_to_remove]

    def select_goals(self, candidate_goals: dict[str, float]):
        """
            Select the goal that is valid based on the textcat score

            :param candidate_goals:
        """
        validated_goal = None

        # For each textcat label (with its score)
        for goal in BASE_GOALS:
            score = candidate_goals[goal.name]

            # If the score equals to 1.0, then the goal is valid
            if score == 1.0:
                print(f'\t{goal.name} {score}')

                # Get the goal
                validated_goal = goal

            else:
                print(colored(f'\t{goal.name} {score}', 'grey'))

        # If a goal was validated
        if validated_goal is not None:
            # Add the goal to the memory
            self.goals.append(validated_goal)

    def fill_answers_and_memory_stack(self):
        """
            Fill the answer list and memory stack with python object by linking the entity and goal lists

            :return:
        """

        for goal in self.goals:
            print('\t', goal.name)

            params_entities_name = []

            # For each entity
            for entity in self.entities:
                entity_label = entity.label_

                # If the label is not present in the available entities
                if entity_label.upper() not in self.ontology.entities:
                    # Then skip it
                    continue

                # Assemble the entity
                assembled_entity = self.assemble_entity(entity)

                # Add the entity to the memory stack
                self.memory_stack[entity_label].append(assembled_entity)

            # For each needed param in this goal
            for param in goal.params:
                # If the param is not present in the memory stack, it means that the param is missing
                if param not in self.memory_stack:
                    raise Exception(f'Missing parameter {param}')
                # Otherwise
                else:
                    # Get the first entity of the memory stack equals to this param
                    params_entities_name.append(self.memory_stack[param][0].name)

            # Call the goal validation function with the retrieved params
            validation_sentence = goal.validation(*params_entities_name)
            # Call the goal finished function with the retrieved params
            finished_sentence = goal.finished(*params_entities_name)

            # Create a goal answer from both
            answer = GoalAnswer(
                validation=validation_sentence,
                finished=finished_sentence
            )

            # Add the answer to the memory
            self.answers.append(answer)

            # For each element of the goal pipeline
            for pipeline_element in goal.pipeline:

                # Match the type of the pipeline element
                match type(pipeline_element):

                    # Task
                    case pipeline.Task:
                        print('\t\t- Task:', pipeline_element.name, pipeline_element.params, '->', pipeline_element.returns)

                    # Condition
                    case pipeline.Condition:
                        print('\t\t- Condition:', pipeline_element.condition_value)

                    # Retrieve Property
                    case pipeline.RetrieveProperty:
                        print('\t\t- Retrieve:', pipeline_element.input_type, '->', pipeline_element.output_type)

    def execute_pipeline(self):
        """
            Execute each goal pipeline

            :return:
        """

        # For each goal
        for goal_index, current_goal in enumerate(self.goals):

            print(colored(f'-------- Goal {goal_index + 1} - {current_goal.name} --------\n', attrs=['bold']))

            # Print the validation sentence
            print('\t>', self.answers[goal_index].validation, '\n')

            # For each pipeline element in the current pipeline
            for pipeline_element_index, current_pipeline_element in enumerate(current_goal.pipeline):

                # Match the pipeline element type
                match type(current_pipeline_element):

                    # Retrieve Property
                    case pipeline.RetrieveProperty:
                        # Call the function that will handle the element
                        self.handle_retrieve_property(index=pipeline_element_index, retrieve_property=current_pipeline_element)

                    # Condition
                    case pipeline.Condition:
                        # Call the function that will handle the element
                        self.handle_condition(index=pipeline_element_index, condition=current_pipeline_element)

                    # Task
                    case pipeline.Task:
                        # Call the function that will handle the element
                        self.handle_task(index=pipeline_element_index, task=current_pipeline_element)

                print('\t\t--------')

            # Print the finished sentence
            print('\t>', self.answers[goal_index].finished)
            print()

    def handle_retrieve_property(self, index: int, retrieve_property: RetrieveProperty):
        """
            Handle a RetrieveProperty pipeline element

            :param index:
            :param retrieve_property:
        """

        print(colored(f'\t\tElement {index + 1} - Retrieving {retrieve_property.output_type} from {retrieve_property.input_type}\n', attrs=['bold']))

        # Get the input type
        input_type = retrieve_property.input_type.__name__.upper()

        # Get the output type
        output_type = retrieve_property.output_type.__name__.upper()

        # Pop the input from the memory stack
        input_value = self.memory_stack[input_type].pop()

        # Retrieve the output from the input
        output_value = retrieve_property.fit(input_value)

        # Push to output into the memory stack
        self.memory_stack[output_type].append(output_value)

    def handle_condition(self, index: int, condition: Condition):
        """
            TODO
            Handle a Condition pipeline element

            :param index:
            :param condition:
        """
        print(colored(f'\t\tElement {index + 1} - Condition {condition.condition_value}', attrs=['bold']))

    def handle_task(self, index: int, task: Task):
        """
            Handle a Task pipeline element

            :param index:
            :param task:
        """

        print(colored(f'\t\tElement {index + 1} - Task {task.name}', attrs=['bold']))

        filled_params = {}

        # For each task param (and its value)
        for param, value in task.params.items():
            # Get the entity label
            entity_label = value.__name__.upper()

            # Pop the value from the memory stack and add it to the filled params
            filled_params[param] = self.memory_stack[entity_label].pop()

        print('\t\t\t> Params:', filled_params, '\n')

        response = None

        # Match the robot middleware
        match self.ontology.robot.middleware:

            # ROS 2
            case Middlewares.ROS2:
                # Recreate the topic name
                topic_name = f'{task.category}/{task.name}'

                # Send the ROS action
                response = send_ros_action(topic_name, filled_params)

            # API
            case Middlewares.API:
                # Recreate the API URL
                url = f'http://127.0.0.1:5000/api/{task.category}/{task.name}'

                # Send the API action
                response = send_api_action(url, filled_params)

        print('\n\t\t\t> Returned:', response, '\n')

        # Match the task return type
        match task.returns:

            # None
            case None:
                pass

            # Boolean
            case builtins.bool:
                if not response:
                    raise Exception(f'Task {task.name} returned false')

            # Any
            case _:
                # Get task return type label
                return_type_label = task.returns.__name__.upper()

                # Append the response to the memory task
                self.memory_stack[return_type_label].append(response)
