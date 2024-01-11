import tomllib

from termcolor import colored

from constants import BASE_TASKS
from models import Ontology, Languages, Robot, Human, Object, InterestPoint, Location, Middlewares, entity_initialisation, ACCEPTED_TYPES, BASE_ENTITIES, ENTITIES_NOT_ALLOWED
from pipeline import Task


class ParseTOMLOntologyException(Exception):
    """
    Raised when something goes wrong while parsing an Ontology TOML file
    """
    pass


def parseOntologyConfig(file_name: str) -> Ontology:
    """
       Parse a TOML ontology file and returns a filled Ontology object

       :param file_name:
       :return:
       """
    print('Parsing Ontology...')

    file = open(file_name, "rb")
    data = tomllib.load(file)

    # === Ontology ===

    ontology = Ontology()

    if 'Ontology' not in data:
        raise ParseTOMLOntologyException('You must provide a "Ontology" table')

    # Ontology > Name

    if 'name' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "name" key/value')

    if not isinstance(data['Ontology']['name'], str):
        raise ParseTOMLOntologyException('The "Ontology.name" parameter value must be a string')

    ontology.name = data['Ontology']['name']

    # Ontology > Description

    if 'description' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "description" key/value')

    if not isinstance(data['Ontology']['description'], str):
        raise ParseTOMLOntologyException('The "Ontology.description" parameter value must be a string')

    ontology.description = data['Ontology']['description']

    # Ontology > Language

    if 'language' not in data['Ontology']:
        raise ParseTOMLOntologyException('The "Ontology" table must have a "language" key/value')

    language_str = data['Ontology']['language']
    languages = [lang.value for lang in Languages]

    if not isinstance(language_str, str):
        raise ParseTOMLOntologyException('The "Ontology.language" parameter value must be a string')

    if not language_str in languages:
        raise ParseTOMLOntologyException(
            f'The "Ontology.language" parameter value "{language_str}" must be a value of the following list: {languages}')

    ontology.name = data['Ontology']['name']

    # === Robot ===

    robot = Robot()

    if 'Robot' not in data:
        raise ParseTOMLOntologyException('You must provide a "Robot" table')

    # Robot > Name

    if 'name' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "name" key/value')

    if not isinstance(data['Robot']['name'], str):
        raise ParseTOMLOntologyException('The "Robot.name" parameter value must be a string')

    robot.name = data['Robot']['name']

    # Robot > Middleware

    if 'middleware' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "middleware" key/value')

    middlewares_str = data['Robot']['middleware']
    middlewares = [middleware.value for middleware in Middlewares]

    if not isinstance(middlewares_str, str):
        raise ParseTOMLOntologyException('The "Robot.middleware" parameter value must be a string')

    if middlewares_str not in middlewares:
        raise ParseTOMLOntologyException(
            f'The "Robot.middleware" parameter value "{middlewares_str}" must be a value of the following list: {middlewares}')

    robot.middleware = Middlewares[middlewares_str]

    ontology.robot = robot

    # Robot > Abilities

    if 'Abilities' not in data['Robot']:
        raise ParseTOMLOntologyException('The "Robot" table must have a "Abilities" table')

    abilities = data['Robot']['Abilities']

    if not isinstance(abilities, dict):
        raise ParseTOMLOntologyException('The "Robot.Abilities" parameter value must be a table')

    for key in abilities:
        if key not in BASE_TASKS.get_categories():
            raise ParseTOMLOntologyException(
                f'The "Robot.Abilities" parameter keys must be in the following list: { [task.name for task in BASE_TASKS.get_categories()] }')

        ability = abilities[key]

        if not isinstance(ability, list):
            raise ParseTOMLOntologyException(f'The "Robot.Abilities" parameter value "{key}" must be an array')

        if len(ability) == 1 and ability[0] == '*':
            tasks = BASE_TASKS.group_by_category(key)
            ontology.available_tasks += tasks
        else:
            for task_name in ability:
                task_found = None

                for task in BASE_TASKS.group_by_category(key):
                    if task_name == task.name:
                        task_found = task

                if task_found is None:
                    raise ParseTOMLOntologyException(
                        f'The "Robot.Abilities.{key}" parameter value "{task_name}" must be in the following list: { [task.name for task in BASE_TASKS]}')

                ontology.available_tasks.append(task_found)

    # === Entities ===

    if 'Entities' not in data:
        raise ParseTOMLOntologyException('The "Robot" table must have a "Entities" table')

    entities = data['Entities']

    if not isinstance(entities, dict):
        raise ParseTOMLOntologyException('The "Ontology.Entities" parameter value must be a table')

    for entity_name in entities:
        capitalized_entity_name = entity_name.capitalize()
        lower_entity_name = entity_name.lower()
        upper_entity_name = entity_name.upper()

        entity = entities[entity_name]

        if not isinstance(entity, dict):
            raise ParseTOMLOntologyException(f'The "Ontology.Entities" parameter value "{capitalized_entity_name}" must be a table')

        if entity_name in ENTITIES_NOT_ALLOWED:
            raise ParseTOMLOntologyException(f'The entity name "{capitalized_entity_name}" is not allowed')
        elif entity_name in BASE_ENTITIES:
            entity_class = eval(capitalized_entity_name)
        else:
            entity_class = type(capitalized_entity_name, (object,), {
                '__module__': 'models',
                '__init__': entity_initialisation,
                'additional_attributes': {}
            })

        for key, value in entity.items():
            upper_key = key.upper()
            capitalized_key = key.capitalize()

            value_type = type(value)

            if value_type not in ACCEPTED_TYPES:
                raise ParseTOMLOntologyException(
                    f'The "Ontology.Entities.{capitalized_entity_name}" parameter value "{key}" type must be in the following list: {ACCEPTED_TYPES}')

            entity_class.additional_attributes[key] = value

            if upper_key not in ontology.NER_labels:
                ontology.NER_labels.append(upper_key)

            ontology.REL_relations.append(f'{capitalized_entity_name}Has{capitalized_key}')

            new_task_params = {lower_entity_name: entity_class}
            new_task = Task(f'get_{key}', lower_entity_name, new_task_params, value_type)
            ontology.available_tasks.append(new_task)

        ontology.entities[upper_entity_name] = entity_class

        if upper_entity_name not in ontology.NER_labels:
            ontology.NER_labels.append(upper_entity_name)

    # ========

    print('Parsing done!')
    # ┌└┐┌
    print('┌——————————————————┐')
    print(f'│ -*- { colored("Ontology", "green", attrs=["bold"])} -*- │')
    print('├——————————————————┘')
    print('│')
    print('│ Name:', ontology.name)
    print('│ Description:', ontology.description)
    print('│ Language:', ontology.language.value)
    print('│')
    print('├————————————┐')
    print(f'│  { colored("Entities", "light_green", attrs=["bold"])}  │')
    print('├————————————┘')
    print('│')
    ontology.print_entities(prefix='│ - ')
    print('│')
    print('├—————————┐')
    print(f'│  { colored("Tasks", "light_green", attrs=["bold"])}  │')
    print('├—————————┘')
    print('│')
    ontology.print_tasks(prefix='│ - ')
    print('└———————————————— ·')

    return ontology
